from abc import ABC, abstractmethod

class TextGenerationProvider(ABC):
    """
    Abstract base class defining the contract for AI text generation.
    Any concrete AI provider (e.g., OpenAI, Anthropic, Gemini) must implement this interface.
    """

    @abstractmethod
    def generate_title(self, topic: str, niche: str) -> str:
        """
        Generate a catchy video title based on the requested topic and channel niche.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_description(self, topic: str, title: str, niche: str) -> str:
        """
        Generate an SEO-friendly video description based on the topic, title, and niche.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_script(self, topic: str, title: str, niche: str) -> str:
        """
        Generate a complete video script matching the given topic, title, and niche.
        """
        raise NotImplementedError

    @abstractmethod
    def generate_hashtags(self, topic: str, title: str, niche: str) -> list[str]:
        """
        Generate a list of relevant hashtags based on the topic, title, and niche.
        """
        raise NotImplementedError
