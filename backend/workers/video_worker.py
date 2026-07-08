import uuid
import logging
from backend.services.job_service import JobService
from backend.services.pipeline_service import PipelineService
from backend.models.job import Job

logger = logging.getLogger(__name__)

class VideoWorker:
    """
    Synchronous execution worker that connects Job execution state with Pipeline orchestration.
    """
    
    def __init__(self, job_service: JobService, pipeline_service: PipelineService):
        self.job_service = job_service
        self.pipeline_service = pipeline_service
        
    def execute(self, job_id: uuid.UUID) -> Job:
        """
        Starts the job, runs the pipeline, and records success or failure.
        Re-raises the original exception if the pipeline fails.
        """
        job = self.job_service.get_job(job_id)
        
        self.job_service.start_job(job_id)
        
        def progress_callback(progress: int, step: str) -> None:
            self.job_service.update_progress(job_id, progress, step)
        
        try:
            self.pipeline_service.process_video(job.video_id, progress_callback=progress_callback)
        except Exception as e:
            original_exc = e
            try:
                self.job_service.fail_job(job_id, str(original_exc))
            except Exception as fail_e:
                logger.error("Failed to persist FAILED job state during exception handling", exc_info=fail_e)
            
            # Re-raise the original pipeline exception
            raise original_exc
            
        return self.job_service.complete_job(job_id)
