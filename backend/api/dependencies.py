from fastapi import Depends
from sqlalchemy.orm import Session

from backend.config.session import get_db
from backend.providers.text.base import TextGenerationProvider
from backend.providers.text.dependency import get_text_provider
from backend.services.video_service import VideoService
from backend.services.dependency import get_video_service, get_job_service, get_audio_service
from backend.services.job_service import JobService
from backend.services.audio_service import AudioService
from backend.providers.audio.base import AudioGenerationProvider
from backend.providers.audio.dependency import get_audio_provider
from backend.services.image_service import ImageService
from backend.providers.image.base import ImageGenerationProvider
from backend.providers.image.dependency import get_image_provider
from backend.services.dependency import get_video_service, get_job_service, get_audio_service, get_image_service

def get_video_service_dependency(
    db: Session = Depends(get_db),
    text_provider: TextGenerationProvider = Depends(get_text_provider),
) -> VideoService:
    """
    FastAPI-specific integration layer for VideoService dependency injection.
    Automatically resolves the database session and the configured text provider,
    then assembles them into a fully configured VideoService for the HTTP request.
    
    Args:
        db: Request-scoped database session injected by FastAPI.
        text_provider: Request-scoped text provider injected by FastAPI.
        
    Returns:
        A ready-to-use VideoService instance.
    """
    return get_video_service(
        db=db,
        text_provider=text_provider,
    )

def get_job_service_dependency(
    db: Session = Depends(get_db),
) -> JobService:
    """
    FastAPI-specific integration layer for JobService dependency injection.
    """
    return get_job_service(db)


def get_audio_service_dependency(
    db: Session = Depends(get_db),
    audio_provider: AudioGenerationProvider = Depends(get_audio_provider),
) -> AudioService:
    """
    FastAPI-specific integration layer for AudioService dependency injection.
    """
    return get_audio_service(
        db=db,
        audio_provider=audio_provider,
    )

def get_image_service_dependency(
    db: Session = Depends(get_db),
    image_provider: ImageGenerationProvider = Depends(get_image_provider),
) -> ImageService:
    """
    FastAPI-specific integration layer for ImageService dependency injection.
    """
    return get_image_service(
        db=db,
        image_provider=image_provider,
    )

