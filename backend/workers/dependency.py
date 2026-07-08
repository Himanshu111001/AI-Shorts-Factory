from backend.services.job_service import JobService
from backend.services.pipeline_service import PipelineService
from backend.workers.video_worker import VideoWorker

def get_video_worker(
    job_service: JobService,
    pipeline_service: PipelineService,
) -> VideoWorker:
    """
    Centralized object assembly for VideoWorker.
    Takes fully resolved domain services and constructs the worker.
    """
    return VideoWorker(
        job_service=job_service,
        pipeline_service=pipeline_service
    )
