from backend.services.pipeline_service import PipelineService
from backend.services.video_service import VideoService
from backend.services.audio_service import AudioService
from backend.services.image_service import ImageService

def get_pipeline_service(
    video_service: VideoService,
    audio_service: AudioService,
    image_service: ImageService,
) -> PipelineService:
    """
    Centralized object assembly for PipelineService.
    Takes fully resolved domain services and constructs the orchestration layer.
    """
    return PipelineService(
        video_service=video_service,
        audio_service=audio_service,
        image_service=image_service,
    )
