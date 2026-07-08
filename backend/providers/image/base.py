from abc import ABC, abstractmethod

class ImageGenerationProvider(ABC):
    """
    Abstract base class defining the contract for AI image generation.
    Any concrete AI image provider must implement this interface.
    """

    @abstractmethod
    def generate_images(
        self,
        prompts: list[str],
        output_dir: str,
    ) -> list[str]:
        """
        Convert text prompts into image files.
        
        Args:
            prompts: The ordered list of text prompts describing the images.
            output_dir: The requested destination directory for the image files.
            
        Returns:
            A list of final image file paths as strings.
        """
        raise NotImplementedError
