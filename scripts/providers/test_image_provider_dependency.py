import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.settings import get_settings
from backend.providers.image.fake import FakeImageGenerationProvider
from backend.providers.image.dependency import get_image_provider

def run_tests():
    print("--- Starting Image Provider Dependency Tests ---")
    
    original_env = os.environ.get("IMAGE_PROVIDER")
    
    try:
        # Clear cache first
        get_settings.cache_clear()
        
        # Test 1
        print("\n[Test 1] Configured provider 'fake'")
        os.environ["IMAGE_PROVIDER"] = "fake"
        get_settings.cache_clear()
        
        provider = get_image_provider()
        if not isinstance(provider, FakeImageGenerationProvider):
            raise AssertionError("Failed to resolve fake provider")
            
        # Test 2
        print("\n[Test 2] Normalized configured value")
        os.environ["IMAGE_PROVIDER"] = "  FaKe  "
        get_settings.cache_clear()
        
        provider2 = get_image_provider()
        if not isinstance(provider2, FakeImageGenerationProvider):
            raise AssertionError("Failed to resolve normalized fake provider")
            
        # Test 3
        print("\n[Test 3] Unsupported configured provider")
        os.environ["IMAGE_PROVIDER"] = "invalid_provider"
        get_settings.cache_clear()
        
        try:
            get_image_provider()
            raise AssertionError("Should have raised ValueError for invalid provider")
        except ValueError as e:
            if "Unsupported image generation provider: invalid_provider" not in str(e):
                raise AssertionError(f"Wrong error message: {e}")
                
        # Test 4
        print("\n[Test 4] get_settings cache behavior")
        os.environ["IMAGE_PROVIDER"] = "fake"
        get_settings.cache_clear()
        
        # Load and cache
        provider_cached1 = get_image_provider()
        if not isinstance(provider_cached1, FakeImageGenerationProvider): raise AssertionError("Setup failed")
        
        # Change env but don't clear cache
        os.environ["IMAGE_PROVIDER"] = "invalid_provider"
        # Since cache is active, it should still return fake
        provider_cached2 = get_image_provider()
        if not isinstance(provider_cached2, FakeImageGenerationProvider):
            raise AssertionError("Cache did not work, it reloaded the environment")
            
        # Now clear cache and it should fail
        get_settings.cache_clear()
        try:
            get_image_provider()
            raise AssertionError("Cache wasn't cleared properly")
        except ValueError:
            pass # Expected
            
    finally:
        # Restore original state
        if original_env is not None:
            os.environ["IMAGE_PROVIDER"] = original_env
        else:
            if "IMAGE_PROVIDER" in os.environ:
                del os.environ["IMAGE_PROVIDER"]
        get_settings.cache_clear()
        
    print("\n--- All Image Provider Dependency Tests Passed ---")

if __name__ == "__main__":
    run_tests()
