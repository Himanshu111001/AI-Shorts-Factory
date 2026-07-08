from backend.providers.text.base import TextGenerationProvider
from backend.providers.text.fake import FakeTextGenerationProvider
from backend.providers.text.gemini import GeminiTextGenerationProvider

class TextProviderFactory:
    """
    Centralized factory for creating text generation provider instances.
    Ensures that services and routes are completely decoupled from concrete provider classes.
    """

    @staticmethod
    def create(provider_name: str) -> TextGenerationProvider:
        """
        Instantiate and return a concrete TextGenerationProvider.
        
        Args:
            provider_name: The name of the AI provider to use.
            
        Returns:
            An instance of a class implementing TextGenerationProvider.
            
        Raises:
            ValueError: If the requested provider is unsupported.
        """
        normalized_name = provider_name.strip().lower()

        if normalized_name == "fake":
            return FakeTextGenerationProvider()
        elif normalized_name == "gemini":
            return GeminiTextGenerationProvider()
        
        raise ValueError(f"Unsupported text generation provider: {provider_name}")
