from backend.providers.image.base import ImageGenerationProvider
from backend.providers.image.fake import FakeImageGenerationProvider

class ImageProviderFactory:
    """
    Centralized factory for creating image generation provider instances.
    Ensures that services and routes are completely decoupled from concrete provider classes.
    """

    @staticmethod
    def create(provider_name: str) -> ImageGenerationProvider:
        """
        Instantiate and return a concrete ImageGenerationProvider.
        """
        normalized_name = provider_name.strip().lower()

        if normalized_name == "fake":
            return FakeImageGenerationProvider()
        
        raise ValueError(f"Unsupported image generation provider: {normalized_name}")
