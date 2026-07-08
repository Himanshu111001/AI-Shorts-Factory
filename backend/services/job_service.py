import uuid
from sqlalchemy.orm import Session
from backend.repositories.job_repository import JobRepository
from backend.repositories.video_repository import VideoRepository
from backend.models.job import Job
from backend.models.enums.job_status import JobStatus
from backend.utils.datetime import utc_now

class JobService:
    """
    Business logic layer for managing background processing jobs.
    Orchestrates validation, state transitions, and repository interactions.
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.job_repo = JobRepository(db)
        self.video_repo = VideoRepository(db)

    def create_job(self, video_id: uuid.UUID) -> Job:
        """
        Create a new job for a video.
        
        Business Rules:
        - The associated video must exist.
        - Prevent duplicate active jobs (QUEUED or RUNNING).
        - Initial status is strictly QUEUED.
        """
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise ValueError("Video not found")
            
        existing_jobs = self.job_repo.get_by_video_id(video_id)
        for job in existing_jobs:
            if job.status in {JobStatus.QUEUED, JobStatus.RUNNING}:
                raise ValueError("Video already has an active job")
                
        job_data = {
            "video_id": video_id,
            "status": JobStatus.QUEUED,
            "progress": 0,
            "current_step": None,
            "error": None
        }
        
        return self.job_repo.create(job_data)

    def start_job(self, job_id: uuid.UUID) -> Job:
        """
        Transition a job from QUEUED to RUNNING.
        Records the started_at timestamp and clears any previous error.
        """
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")
            
        if job.status != JobStatus.QUEUED:
            raise ValueError(f"Invalid job status transition: {job.status.value} -> RUNNING")
            
        # Using generic update to explicitly clear error=None since update_status ignores None
        update_data = {
            "status": JobStatus.RUNNING,
            "started_at": utc_now(),
            "error": None
        }
        return self.job_repo.update(job_id, update_data)

    def update_progress(self, job_id: uuid.UUID, progress: int, current_step: str | None = None) -> Job:
        """
        Update the progress of a RUNNING job.
        
        Business Rules:
        - Job must be RUNNING.
        - Progress must be between 0 and 100.
        """
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")
            
        if job.status != JobStatus.RUNNING:
            raise ValueError("Job progress can only be updated while RUNNING")
            
        if not (0 <= progress <= 100):
            raise ValueError("Job progress must be between 0 and 100")
            
        return self.job_repo.update_progress(job_id, progress, current_step)

    def complete_job(self, job_id: uuid.UUID) -> Job:
        """
        Transition a job from RUNNING to COMPLETED.
        Sets progress to 100, clears error, and records finished_at.
        """
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")
            
        if job.status != JobStatus.RUNNING:
            raise ValueError(f"Invalid job status transition: {job.status.value} -> COMPLETED")
            
        update_data = {
            "status": JobStatus.COMPLETED,
            "progress": 100,
            "current_step": "Completed",
            "finished_at": utc_now(),
            "error": None
        }
        return self.job_repo.update(job_id, update_data)

    def fail_job(self, job_id: uuid.UUID, error: str) -> Job:
        """
        Transition a job from RUNNING to FAILED.
        Records the failure reason and finished_at timestamp.
        """
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")
            
        if job.status != JobStatus.RUNNING:
            raise ValueError(f"Invalid job status transition: {job.status.value} -> FAILED")
            
        return self.job_repo.update_status(
            job_id,
            status=JobStatus.FAILED,
            finished_at=utc_now(),
            error=error
        )

    def get_job(self, job_id: uuid.UUID) -> Job:
        """
        Retrieve a job by ID.
        Raises ValueError if not found.
        """
        job = self.job_repo.get_by_id(job_id)
        if not job:
            raise ValueError("Job not found")
        return job

    def get_jobs_for_video(self, video_id: uuid.UUID) -> list[Job]:
        """
        Retrieve all jobs for a video.
        Raises ValueError if the video is not found.
        """
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise ValueError("Video not found")
            
        return self.job_repo.get_by_video_id(video_id)
