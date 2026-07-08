import os
import sys
import traceback

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.settings import get_settings
from backend.providers.text.dependency import get_text_provider
from backend.providers.text.base import TextGenerationProvider
from backend.providers.text.fake import FakeTextGenerationProvider

def run_tests():
    print("--- Starting Text Provider Dependency Resolver Verification ---")
    
    # Save original state so we can restore it cleanly
    original_text_provider = os.environ.get("TEXT_PROVIDER")
    
    try:
        # Test 1: Valid configured provider
        print("\n[Test 1] Valid configured provider ('fake')")
        os.environ["TEXT_PROVIDER"] = "fake"
        get_settings.cache_clear()
        
        provider1 = get_text_provider()
        if not isinstance(provider1, TextGenerationProvider):
            raise AssertionError("provider1 does not inherit from TextGenerationProvider")
        if not isinstance(provider1, FakeTextGenerationProvider):
            raise AssertionError("provider1 is not an instance of FakeTextGenerationProvider")
        print("  -> PASS")

        # Test 2: Configuration normalization through the complete resolver chain
        print("\n[Test 2] Configuration normalization through resolver chain ('  FaKe ')")
        os.environ["TEXT_PROVIDER"] = "  FaKe "
        get_settings.cache_clear()
        
        provider2 = get_text_provider()
        if not isinstance(provider2, FakeTextGenerationProvider):
            raise AssertionError("provider2 is not an instance of FakeTextGenerationProvider")
        print("  -> PASS")

        # Test 3: Unsupported configured provider
        print("\n[Test 3] Unsupported configured provider")
        os.environ["TEXT_PROVIDER"] = "unsupported_provider"
        get_settings.cache_clear()
        
        try:
            get_text_provider()
            raise AssertionError("Allowed creation of unsupported provider")
        except ValueError as e:
            expected_msg = "Unsupported text generation provider: unsupported_provider"
            if str(e) != expected_msg:
                raise AssertionError(f"Expected error '{expected_msg}', got '{e}'")
            print("  -> PASS")

        # Test 4: Settings cache interaction
        print("\n[Test 4] Settings cache interaction")
        os.environ["TEXT_PROVIDER"] = "fake"
        get_settings.cache_clear()
        
        # Load it once to populate the cache
        provider_cached = get_text_provider()
        if not isinstance(provider_cached, FakeTextGenerationProvider):
            raise AssertionError("Failed to load fake provider for cache test")
            
        # Change environment but do NOT clear the cache
        os.environ["TEXT_PROVIDER"] = "unsupported_provider"
        
        provider_still_cached = get_text_provider()
        if not isinstance(provider_still_cached, FakeTextGenerationProvider):
            raise AssertionError("Resolver failed to use cached settings")
        print("  -> PASS (Cached settings preserved)")
        
        # Now clear the cache and verify it fails as expected
        get_settings.cache_clear()
        try:
            get_text_provider()
            raise AssertionError("Allowed creation of unsupported provider after cache clear")
        except ValueError as e:
            expected_msg = "Unsupported text generation provider: unsupported_provider"
            if str(e) != expected_msg:
                raise AssertionError(f"Expected error '{expected_msg}', got '{e}'")
            print("  -> PASS (Cache refresh succeeded)")
            
    except Exception as e:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        raise
        
    finally:
        print("\n[Cleanup] Restoring original environment and resetting cache...")
        if original_text_provider is not None:
            os.environ["TEXT_PROVIDER"] = original_text_provider
        else:
            if "TEXT_PROVIDER" in os.environ:
                del os.environ["TEXT_PROVIDER"]
                
        get_settings.cache_clear()
        
    print("--- All tests passed! Text Provider Dependency works as expected. ---")

if __name__ == "__main__":
    run_tests()
