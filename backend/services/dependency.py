from sqlalchemy.orm import Session
from backend.services.video_service import VideoService
from backend.providers.text.base import TextGenerationProvider
from backend.services.job_service import JobService
from backend.services.audio_service import AudioService
from backend.services.image_service import ImageService
from backend.providers.audio.base import AudioGenerationProvider
from backend.providers.image.base import ImageGenerationProvider
from backend.services.render_service import RenderService
from backend.providers.render.base import RenderProvider

def get_video_service(
    db: Session,
    text_provider: TextGenerationProvider,
) -> VideoService:
    """
    Centralized application-level object assembly for VideoService.
    Takes fully resolved dependencies (database connection and text AI provider)
    and constructs the business service layer.
    
    Args:
        db: An active SQLAlchemy Session.
        text_provider: A fully resolved TextGenerationProvider instance.
        
    Returns:
        A fully configured VideoService ready for execution.
    """
    return VideoService(
        db=db,
        text_provider=text_provider,
    )

def get_job_service(db: Session) -> JobService:
    """
    Centralized object assembly for JobService.
    """
    return JobService(db)


def get_audio_service(
    db: Session,
    audio_provider: AudioGenerationProvider,
) -> AudioService:
    """
    Centralized application-level object assembly for AudioService.
    """
    return AudioService(
        db=db,
        audio_provider=audio_provider,
    )

def get_image_service(
    db: Session,
    image_provider: ImageGenerationProvider,
) -> ImageService:
    """
    Centralized application-level object assembly for ImageService.
    """
    return ImageService(
        db=db,
        image_provider=image_provider,
    )

def get_render_service(
    db: Session,
    render_provider: RenderProvider,
) -> RenderService:
    """
    Centralized application-level object assembly for RenderService.
    """
    return RenderService(
        db=db,
        render_provider=render_provider,
    )
