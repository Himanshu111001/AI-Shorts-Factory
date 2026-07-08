from backend.config.settings import get_settings
from backend.providers.image.base import ImageGenerationProvider
from backend.providers.image.factory import ImageProviderFactory

def get_image_provider() -> ImageGenerationProvider:
    """
    Application-level dependency resolver for the image generation provider.
    Reads configuration and delegates instantiation to the factory.
    
    Returns:
        An instance of a concrete ImageGenerationProvider.
    """
    settings = get_settings()
    return ImageProviderFactory.create(settings.image_provider)
