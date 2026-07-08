import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from backend.repositories.video_repository import VideoRepository
from backend.models.video import Video
from backend.providers.audio.base import AudioGenerationProvider
from backend.config.settings import get_settings

class AudioService:
    """
    Business logic layer for managing Video audio generation.
    """

    def __init__(
        self,
        db: Session,
        audio_provider: AudioGenerationProvider | None = None,
    ):
        self.db = db
        self.video_repo = VideoRepository(db)
        self.audio_provider = audio_provider

    def generate_audio(self, video_id: uuid.UUID) -> Video:
        """
        Generate and persist the narration audio for a video.
        """
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise ValueError("Video not found")

        if video.script is None or video.script.strip() == "":
            raise ValueError("Audio generation requires generated script")

        if self.audio_provider is None:
            raise ValueError("Audio generation provider is not configured")

        settings = get_settings()
        storage_root = Path(settings.storage_path)
        
        # Conceptual path: <storage_path>/videos/<video_id>/narration.fake
        output_path = storage_root / "videos" / str(video_id) / "narration.fake"

        # Generate audio (provider handles dir creation if needed)
        generated_audio_path = self.audio_provider.generate_audio(
            text=video.script,
            output_path=str(output_path),
        )

        # Update persistence
        updated_video = self.video_repo.update(
            video_id,
            {
                "audio_path": generated_audio_path
            }
        )

        return updated_video
