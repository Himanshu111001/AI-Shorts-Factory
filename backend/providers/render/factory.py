from backend.providers.render.base import RenderProvider
from backend.providers.render.fake import FakeRenderProvider

class RenderProviderFactory:
    """
    Centralized factory for creating render provider instances.
    Ensures that services and routes are completely decoupled from concrete provider classes.
    """

    @staticmethod
    def create(provider_name: str) -> RenderProvider:
        """
        Instantiate and return a concrete RenderProvider.
        """
        normalized_name = provider_name.strip().lower()

        if normalized_name == "fake":
            return FakeRenderProvider()
        
        raise ValueError(f"Unsupported render provider: {normalized_name}")
