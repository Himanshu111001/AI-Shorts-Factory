import os
import sys
import traceback

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.settings import get_settings
from backend.providers.audio.dependency import get_audio_provider
from backend.providers.audio.base import AudioGenerationProvider
from backend.providers.audio.fake import FakeAudioGenerationProvider

def run_tests():
    print("--- Starting Audio Provider Dependency Resolver Verification ---")
    
    # Save original state so we can restore it cleanly
    original_audio_provider = os.environ.get("AUDIO_PROVIDER")
    
    try:
        # Test 1: Valid configured provider
        print("\n[Test 1] Valid configured provider ('fake')")
        os.environ["AUDIO_PROVIDER"] = "fake"
        get_settings.cache_clear()
        
        provider1 = get_audio_provider()
        if not isinstance(provider1, AudioGenerationProvider):
            raise AssertionError("provider1 does not inherit from AudioGenerationProvider")
        if not isinstance(provider1, FakeAudioGenerationProvider):
            raise AssertionError("provider1 is not an instance of FakeAudioGenerationProvider")
        print("  -> PASS")

        # Test 2: Configuration normalization through the complete resolver chain
        print("\n[Test 2] Configuration normalization through resolver chain ('  FaKe  ')")
        os.environ["AUDIO_PROVIDER"] = "  FaKe  "
        get_settings.cache_clear()
        
        provider2 = get_audio_provider()
        if not isinstance(provider2, FakeAudioGenerationProvider):
            raise AssertionError("provider2 is not an instance of FakeAudioGenerationProvider")
        print("  -> PASS")

        # Test 3: Unsupported configured provider
        print("\n[Test 3] Unsupported configured provider")
        os.environ["AUDIO_PROVIDER"] = "elevenlabs"
        get_settings.cache_clear()
        
        try:
            get_audio_provider()
            raise AssertionError("Allowed creation of unsupported provider")
        except ValueError as e:
            expected_msg = "Unsupported audio generation provider: elevenlabs"
            if str(e) != expected_msg:
                raise AssertionError(f"Expected error '{expected_msg}', got '{e}'")
            print("  -> PASS")

        # Test 4: Settings cache interaction
        print("\n[Test 4] Settings cache interaction")
        os.environ["AUDIO_PROVIDER"] = "fake"
        get_settings.cache_clear()
        
        # Load it once to populate the cache
        provider_cached = get_audio_provider()
        if not isinstance(provider_cached, FakeAudioGenerationProvider):
            raise AssertionError("Failed to load fake provider for cache test")
            
        # Change environment but do NOT clear the cache
        os.environ["AUDIO_PROVIDER"] = "elevenlabs"
        
        provider_still_cached = get_audio_provider()
        if not isinstance(provider_still_cached, FakeAudioGenerationProvider):
            raise AssertionError("Resolver failed to use cached settings")
        print("  -> PASS (Cached settings preserved)")
        
        # Now clear the cache and verify it fails as expected
        get_settings.cache_clear()
        try:
            get_audio_provider()
            raise AssertionError("Allowed creation of unsupported provider after cache clear")
        except ValueError as e:
            expected_msg = "Unsupported audio generation provider: elevenlabs"
            if str(e) != expected_msg:
                raise AssertionError(f"Expected error '{expected_msg}', got '{e}'")
            print("  -> PASS (Cache refresh succeeded)")
            
    except Exception:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        raise
        
    finally:
        print("\n[Cleanup] Restoring original environment and resetting cache...")
        if original_audio_provider is not None:
            os.environ["AUDIO_PROVIDER"] = original_audio_provider
        else:
            if "AUDIO_PROVIDER" in os.environ:
                del os.environ["AUDIO_PROVIDER"]
                
        get_settings.cache_clear()
        
    print("\n--- All tests passed! Audio Provider Dependency works as expected. ---")

if __name__ == "__main__":
    run_tests()
