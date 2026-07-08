from abc import ABC, abstractmethod

class RenderProvider(ABC):
    """
    Abstract base class defining the contract for AI video rendering.
    Any concrete render provider must implement this interface.
    """

    @abstractmethod
    def render_video(
        self,
        audio_path: str,
        image_paths: list[str],
        output_path: str,
    ) -> str:
        """
        Combine an audio track and ordered images into a final video artifact.
        
        Args:
            audio_path: Path to the narration audio artifact.
            image_paths: Ordered list of generated image artifact paths.
            output_path: Requested destination path for the final rendered video artifact.
            
        Returns:
            The final rendered video artifact path as a string.
        """
        raise NotImplementedError
