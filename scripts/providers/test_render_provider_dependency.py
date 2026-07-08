import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.settings import get_settings
from backend.providers.render.dependency import get_render_provider
from backend.providers.render.fake import FakeRenderProvider

def run_tests():
    print("--- Starting Render Provider Dependency Tests ---")
    
    original_provider = os.environ.get("RENDER_PROVIDER")
    
    try:
        print("\n[Test 1] Default or Configured Fake Provider")
        os.environ["RENDER_PROVIDER"] = "fake"
        get_settings.cache_clear()
        provider = get_render_provider()
        if not isinstance(provider, FakeRenderProvider):
            raise AssertionError(f"Expected FakeRenderProvider, got {type(provider)}")
            
        print("\n[Test 2] Normalization")
        os.environ["RENDER_PROVIDER"] = "  FaKe  "
        get_settings.cache_clear()
        provider2 = get_render_provider()
        if not isinstance(provider2, FakeRenderProvider):
            raise AssertionError(f"Expected FakeRenderProvider, got {type(provider2)}")
            
        print("\n[Test 3] Unsupported Configuration")
        os.environ["RENDER_PROVIDER"] = "ffmpeg"
        get_settings.cache_clear()
        try:
            get_render_provider()
            raise AssertionError("Should have raised ValueError for ffmpeg")
        except ValueError as e:
            if str(e) != "Unsupported render provider: ffmpeg":
                raise AssertionError(f"Wrong error: {e}")
                
        print("\n[Test 4] Settings Cache Behavior")
        os.environ["RENDER_PROVIDER"] = "fake"
        get_settings.cache_clear()
        _ = get_render_provider()
        
        # Change env but don't clear cache
        os.environ["RENDER_PROVIDER"] = "ffmpeg"
        # Should still work because settings are cached
        provider_cached = get_render_provider()
        if not isinstance(provider_cached, FakeRenderProvider):
            raise AssertionError("Cache was not respected")
            
        # Now clear cache, it should read ffmpeg and fail
        get_settings.cache_clear()
        try:
            get_render_provider()
            raise AssertionError("Cache clear did not reload settings")
        except ValueError:
            pass
            
    finally:
        if original_provider is not None:
            os.environ["RENDER_PROVIDER"] = original_provider
        else:
            if "RENDER_PROVIDER" in os.environ:
                del os.environ["RENDER_PROVIDER"]
        get_settings.cache_clear()

    print("\n--- All Render Provider Dependency Tests Passed! ---")

if __name__ == "__main__":
    run_tests()
