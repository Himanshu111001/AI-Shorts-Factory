from backend.config.settings import get_settings
from backend.providers.text.base import TextGenerationProvider
from backend.providers.text.factory import TextProviderFactory

def get_text_provider() -> TextGenerationProvider:
    """
    Application-level dependency resolver for the text generation provider.
    Reads configuration and delegates instantiation to the factory.
    
    Returns:
        An instance of a concrete TextGenerationProvider.
    """
    settings = get_settings()
    return TextProviderFactory.create(settings.text_provider)
