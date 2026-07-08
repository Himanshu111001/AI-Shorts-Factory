import uuid
from pathlib import Path
from sqlalchemy.orm import Session
from backend.repositories.video_repository import VideoRepository
from backend.repositories.generated_image_repository import GeneratedImageRepository
from backend.models.video import Video
from backend.providers.render.base import RenderProvider
from backend.config.settings import get_settings

class RenderService:
    """
    Business logic layer for managing Video rendering.
    """

    def __init__(
        self,
        db: Session,
        render_provider: RenderProvider | None = None,
    ):
        self.db = db
        self.video_repo = VideoRepository(db)
        self.image_repo = GeneratedImageRepository(db)
        self.render_provider = render_provider

    def render_video(self, video_id: uuid.UUID) -> Video:
        """
        Combine generated audio and ordered generated images into a final video artifact.
        """
        # 1. Fetch Video
        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise ValueError("Video not found")

        # 2. Validate audio path
        if not video.audio_path or not video.audio_path.strip():
            raise ValueError("Video rendering requires generated audio")

        # 3. Load generated images
        images = self.image_repo.get_by_video_id(video_id)
        if not images:
            raise ValueError("Video rendering requires generated images")

        # 4. Extract and validate image paths
        image_paths = []
        for image in images:
            if not image.file_path or not image.file_path.strip():
                raise ValueError("Generated image contains invalid file path")
            image_paths.append(image.file_path)

        # 5. Validate provider
        if self.render_provider is None:
            raise ValueError("Render provider is not configured")

        # 6. Construct output path
        settings = get_settings()
        storage_root = Path(settings.storage_path)
        output_path = storage_root / "videos" / str(video_id) / "final.fake"

        # 7. Call provider
        # Allowed to raise exception, in which case we don't update db.
        generated_video_path = self.render_provider.render_video(
            audio_path=video.audio_path,
            image_paths=image_paths,
            output_path=str(output_path),
        )

        # 8. Validate provider result
        if not isinstance(generated_video_path, str) or not generated_video_path.strip():
            raise ValueError("Render provider returned invalid output path")

        # 9. Persist result
        updated_video = self.video_repo.update(
            video_id,
            {
                "rendered_video_path": generated_video_path
            }
        )

        return updated_video
