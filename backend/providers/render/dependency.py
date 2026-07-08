from backend.config.settings import get_settings
from backend.providers.render.base import RenderProvider
from backend.providers.render.factory import RenderProviderFactory

def get_render_provider() -> RenderProvider:
    """
    Application-level dependency resolver for the render provider.
    Reads configuration and delegates instantiation to the factory.
    
    Returns:
        An instance of a concrete RenderProvider.
    """
    settings = get_settings()
    return RenderProviderFactory.create(settings.render_provider)
