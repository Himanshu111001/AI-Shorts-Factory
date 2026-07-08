from backend.config.settings import get_settings
from backend.providers.audio.base import AudioGenerationProvider
from backend.providers.audio.factory import AudioProviderFactory

def get_audio_provider() -> AudioGenerationProvider:
    """
    Application-level dependency resolver for the audio generation provider.
    Reads configuration and delegates instantiation to the factory.
    
    Returns:
        An instance of a concrete AudioGenerationProvider.
    """
    settings = get_settings()
    return AudioProviderFactory.create(settings.audio_provider)
