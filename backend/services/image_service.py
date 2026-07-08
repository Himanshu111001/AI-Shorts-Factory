import uuid
import re
from typing import List
from pathlib import Path
from sqlalchemy.orm import Session

from backend.models.generated_image import GeneratedImage
from backend.repositories.video_repository import VideoRepository
from backend.repositories.generated_image_repository import GeneratedImageRepository
from backend.providers.image.base import ImageGenerationProvider
from backend.config.settings import get_settings

class ImageService:
    """
    Orchestrates the conversion of generated Video scripts into ordered scene images.
    """

    def __init__(self, db: Session, image_provider: ImageGenerationProvider):
        """
        Initialize the service with active dependencies.
        """
        self.db = db
        self.image_provider = image_provider
        self.video_repo = VideoRepository(db)
        self.image_repo = GeneratedImageRepository(db)

    def _plan_scene_prompts(self, script: str, image_count: int) -> List[str]:
        """
        Deterministically segment the script into ordered scene prompts.
        """
        if not script or not script.strip():
            raise ValueError("Script is empty")

        text = script.strip()
        text = re.sub(r'\s+', ' ', text)
        
        # Simple deterministic sentence splitting
        sentences = [s.strip() for s in re.split(r'[.!?]', text) if s.strip()]
        if not sentences:
            sentences = [text]

        prompts = []
        for i in range(1, image_count + 1):
            # Wrap around deterministically if we have fewer sentences than images
            idx = (i - 1) % len(sentences)
            scene_text = sentences[idx]
            
            prompt = (
                f"Create a cinematic vertical 9:16 visual for scene {i} of a YouTube Short.\n"
                f"Scene content: {scene_text}\n"
                f"No text overlays, captions, logos, or watermarks."
            )
            prompts.append(prompt)
            
        return prompts

    def generate_images(self, video_id: uuid.UUID, image_count: int = 4) -> List[GeneratedImage]:
        """
        Plan and generate images for a Video.
        Replaces any existing images atomically on success.
        """
        if not self.image_provider:
            raise ValueError("Image generation provider is not configured")

        if image_count <= 0:
            raise ValueError("Image count must be greater than 0")

        video = self.video_repo.get_by_id(video_id)
        if not video:
            raise ValueError("Video not found")

        if not video.script or not video.script.strip():
            raise ValueError("Image generation requires generated script")

        # 1. Plan scene prompts
        prompts = self._plan_scene_prompts(video.script, image_count)
        
        # 2. Configure output directory
        settings = get_settings()
        output_dir = str(Path(settings.storage_path) / "videos" / str(video_id) / "images")

        # 3. Call Provider
        paths = self.image_provider.generate_images(prompts, output_dir)
        
        # 4. Validate Provider Result
        if not isinstance(paths, list):
            raise ValueError("Image provider returned invalid result")
            
        if len(paths) != len(prompts):
            raise ValueError("Image provider returned invalid result")
            
        for path in paths:
            if not path or not path.strip():
                raise ValueError("Image provider returned invalid result")

        # 5. Persist Replace Data
        images_data = []
        for i, (prompt, path) in enumerate(zip(prompts, paths), 1):
            images_data.append({
                "video_id": video_id,
                "sequence_index": i,
                "prompt": prompt,
                "file_path": path
            })

        return self.image_repo.replace_for_video(video_id, images_data)
