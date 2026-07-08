import os
import sys
import traceback

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.settings import Settings, get_settings

def run_tests():
    print("--- Starting Text Provider Settings Verification ---")
    
    # Save original state so we can restore it cleanly
    original_text_provider = os.environ.get("TEXT_PROVIDER")
    
    try:
        # Test 1: Class default value (isolated from environment and .env)
        print("\n[Test 1] Class default value isolation")
        # Ensure the OS environment is completely cleared of this key
        if "TEXT_PROVIDER" in os.environ:
            del os.environ["TEXT_PROVIDER"]
            
        # Passing _env_file=None to Pydantic prevents it from loading the local .env file
        isolated_settings = Settings(_env_file=None)
        
        if isolated_settings.text_provider != "fake":
            raise AssertionError(f"Expected isolated default 'fake', got '{isolated_settings.text_provider}'")
        print("  -> PASS: Default value is 'fake'")

        # Test 2: Environment override
        print("\n[Test 2] Environment override")
        os.environ["TEXT_PROVIDER"] = "custom_test_provider"
        # Again pass _env_file=None so only OS environment is used
        env_settings = Settings(_env_file=None)
        
        if env_settings.text_provider != "custom_test_provider":
            raise AssertionError(f"Expected 'custom_test_provider', got '{env_settings.text_provider}'")
        print("  -> PASS: Environment variable override successfully intercepts the default")

        # Test 3: get_settings cache behavior
        print("\n[Test 3] get_settings cache behavior")
        get_settings.cache_clear()
        
        # Populate a value and trigger the first evaluation
        os.environ["TEXT_PROVIDER"] = "fake"
        cached_settings_1 = get_settings()
        if cached_settings_1.text_provider != "fake":
            raise AssertionError(f"Expected initial cached load to be 'fake', got '{cached_settings_1.text_provider}'")
            
        # Change the environment variable AFTER the settings are cached
        os.environ["TEXT_PROVIDER"] = "changed_after_cache"
        
        # Request settings again; it should STILL return 'fake' due to @lru_cache
        cached_settings_2 = get_settings()
        if cached_settings_2.text_provider != "fake":
            raise AssertionError(f"Cache failed! Expected 'fake', but picked up live env var '{cached_settings_2.text_provider}'")
        print("  -> PASS: get_settings securely caches configuration in memory")

        # Test 4: Cache refresh behavior
        print("\n[Test 4] Cache refresh behavior")
        get_settings.cache_clear()
        
        # Request settings again; cache is wiped, so it should read the new live value
        cached_settings_3 = get_settings()
        if cached_settings_3.text_provider != "changed_after_cache":
            raise AssertionError(f"Cache clear failed! Expected 'changed_after_cache', got '{cached_settings_3.text_provider}'")
        print("  -> PASS: get_settings reliably picks up new values after cache_clear()")

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
        print("--- Text Provider Settings Tests Complete ---")

if __name__ == "__main__":
    run_tests()
