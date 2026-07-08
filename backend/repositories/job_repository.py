import uuid
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from backend.models.job import Job
from backend.models.enums.job_status import JobStatus

class JobRepository:
    """
    Repository for managing Job entities in the database.
    Handles all CRUD operations directly via SQLAlchemy 2.0 conventions.
    """

    def __init__(self, db: Session):
        """
        Initialize the repository with an active SQLAlchemy Session.
        """
        self.db = db

    def create(self, job_data: dict) -> Job:
        """
        Create a new job record.
        """
        job = Job(**job_data)
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_by_id(self, job_id: uuid.UUID) -> Optional[Job]:
        """
        Retrieve a job by its UUID.
        """
        stmt = select(Job).where(Job.id == job_id)
        return self.db.execute(stmt).scalar_one_or_none()

    def get_by_video_id(self, video_id: uuid.UUID) -> list[Job]:
        """
        Retrieve all jobs associated with a video, ordered by created_at descending.
        """
        stmt = select(Job).where(Job.video_id == video_id).order_by(desc(Job.created_at))
        return list(self.db.execute(stmt).scalars().all())

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Job]:
        """
        Retrieve a list of jobs with optional pagination.
        """
        stmt = select(Job).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def update(self, job_id: uuid.UUID, update_data: dict) -> Job:
        """
        Update an existing job's generic attributes.
        Raises ValueError if the job is not found, consistent with other repositories.
        """
        job = self.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job with id {job_id} not found.")

        for key, value in update_data.items():
            setattr(job, key, value)
            
        self.db.commit()
        self.db.refresh(job)
        return job

    def delete(self, job_id: uuid.UUID) -> bool:
        """
        Delete a job by its UUID.
        Raises ValueError if the job is not found, consistent with other repositories.
        """
        job = self.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job with id {job_id} not found.")

        self.db.delete(job)
        self.db.commit()
        return True

    def update_status(
        self,
        job_id: uuid.UUID,
        status: JobStatus,
        *,
        started_at=None,
        finished_at=None,
        error=None
    ) -> Job:
        """
        Focused method to update the job's execution status and relevant timestamps.
        Does NOT validate state transitions (e.g. QUEUED -> RUNNING) - that is business logic.
        """
        job = self.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job with id {job_id} not found.")
            
        job.status = status
        
        if started_at is not None:
            job.started_at = started_at
        if finished_at is not None:
            job.finished_at = finished_at
        if error is not None:
            job.error = error
            
        self.db.commit()
        self.db.refresh(job)
        return job

    def update_progress(
        self,
        job_id: uuid.UUID,
        progress: int,
        current_step: Optional[str] = None
    ) -> Job:
        """
        Focused method to update the job's completion progress and current step description.
        Relies on the database constraint for final progress range enforcement (0-100).
        """
        job = self.get_by_id(job_id)
        if not job:
            raise ValueError(f"Job with id {job_id} not found.")
            
        job.progress = progress
        if current_step is not None:
            job.current_step = current_step
            
        self.db.commit()
        self.db.refresh(job)
        return job
