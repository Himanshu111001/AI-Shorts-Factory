import uuid
from typing import Callable
from backend.services.video_service import VideoService
from backend.services.audio_service import AudioService
from backend.services.image_service import ImageService
from backend.services.render_service import RenderService
from backend.models.video import Video

class PipelineService:
    """
    Orchestrates the entire AI media generation pipeline.
    Delegates business rules and actual execution to specific domain services.
    """
    def __init__(
        self,
        video_service: VideoService,
        audio_service: AudioService,
        image_service: ImageService,
        render_service: RenderService,
    ):
        self.video_service = video_service
        self.audio_service = audio_service
        self.image_service = image_service
        self.render_service = render_service

    def generate_text(self, video_id: uuid.UUID) -> Video:
        """Orchestrates the text generation phase."""
        return self.video_service.generate_text_content(video_id)

    # Future stages will be inserted here:
    # def generate_audio(self, video_id: uuid.UUID) -> Video:
    #     return self.audio_service.generate_audio_content(video_id)
    #
    # def generate_images(self, video_id: uuid.UUID) -> Video:
    #     return self.image_service.generate_images(video_id)
    #
    # def render_video(self, video_id: uuid.UUID) -> Video:
    #     return self.render_service.render(video_id)
    #
    # def upload_video(self, video_id: uuid.UUID) -> Video:
    #     return self.upload_service.upload(video_id)

    def _report_progress(
        self,
        callback: Callable[[int, str], None] | None,
        progress: int,
        step: str,
    ) -> None:
        if callback is not None:
            callback(progress, step)

    def process_video(
        self, 
        video_id: uuid.UUID,
        progress_callback: Callable[[int, str], None] | None = None,
    ) -> Video:
        """
        Executes the full pipeline sequentially.
        """
        # Step 1: Text Generation
        self._report_progress(progress_callback, 10, "Generating Text")
        video = self.video_service.generate_text_content(video_id)
        self._report_progress(progress_callback, 30, "Text Generated")
        
        # Step 2: Audio Generation
        self._report_progress(progress_callback, 35, "Generating Audio")
        video = self.audio_service.generate_audio(video_id)
        self._report_progress(progress_callback, 50, "Audio Generated")
        
        # Step 3: Image Generation
        self._report_progress(progress_callback, 55, "Generating Images")
        images = self.image_service.generate_images(video_id)
        self._report_progress(progress_callback, 75, "Images Generated")
        
        # Step 4: Render Video
        self._report_progress(progress_callback, 80, "Rendering Video")
        video = self.render_service.render_video(video_id)
        self._report_progress(progress_callback, 95, "Video Rendered")
        
        return video
