from backend.providers.audio.base import AudioGenerationProvider
from backend.providers.audio.fake import FakeAudioGenerationProvider

class AudioProviderFactory:
    """
    Centralized factory for creating audio generation provider instances.
    Ensures that services and routes are completely decoupled from concrete provider classes.
    """

    @staticmethod
    def create(provider_name: str) -> AudioGenerationProvider:
        """
        Instantiate and return a concrete AudioGenerationProvider.
        """
        normalized_name = provider_name.strip().lower()

        if normalized_name == "fake":
            return FakeAudioGenerationProvider()
        
        raise ValueError(f"Unsupported audio generation provider: {normalized_name}")
