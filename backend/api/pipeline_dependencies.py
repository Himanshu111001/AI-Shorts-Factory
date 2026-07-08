from fastapi import Depends
from backend.services.pipeline_service import PipelineService
from backend.services.pipeline_dependency import get_pipeline_service
from backend.services.video_service import VideoService
from backend.services.audio_service import AudioService
from backend.services.image_service import ImageService
from backend.api.dependencies import get_video_service_dependency, get_job_service_dependency, get_audio_service_dependency, get_image_service_dependency
from backend.workers.video_worker import VideoWorker
from backend.workers.dependency import get_video_worker
from backend.services.job_service import JobService

def get_pipeline_service_dependency(
    video_service: VideoService = Depends(get_video_service_dependency),
    audio_service: AudioService = Depends(get_audio_service_dependency),
    image_service: ImageService = Depends(get_image_service_dependency),
) -> PipelineService:
    """
    FastAPI integration layer for PipelineService dependency injection.
    Automatically resolves the underlying VideoService and AudioService and constructs the PipelineService.
    """
    return get_pipeline_service(
        video_service=video_service,
        audio_service=audio_service,
        image_service=image_service,
    )

def get_video_worker_dependency(
    job_service: JobService = Depends(get_job_service_dependency),
    pipeline_service: PipelineService = Depends(get_pipeline_service_dependency),
) -> VideoWorker:
    """
    FastAPI integration layer for VideoWorker dependency injection.
    Automatically resolves JobService and PipelineService to construct the worker.
    """
    return get_video_worker(
        job_service=job_service,
        pipeline_service=pipeline_service,
    )

