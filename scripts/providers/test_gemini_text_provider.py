import os
import sys
import traceback

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.settings import get_settings

try:
    from backend.providers.text.gemini import GeminiTextGenerationProvider
except ImportError:
    # If the user hasn't installed google-genai, gracefully catch it.
    GeminiTextGenerationProvider = None

def run_tests():
    print("--- Starting GeminiTextGenerationProvider Integration Tests ---")
    
    settings = get_settings()
    
    if not settings.gemini_api_key:
        print("\n[SKIPPED] GEMINI_API_KEY is not configured in environment or .env. Skipping real Gemini API tests.")
        # Exit with 0 so the runner script doesn't fail the entire suite
        sys.exit(0)
        
    if not GeminiTextGenerationProvider:
        print("\n[SKIPPED] google-genai SDK is not installed. Skipping real Gemini API tests.")
        sys.exit(0)
        
    try:
        print("\n[Setup] Initializing Gemini Provider...")
        provider = GeminiTextGenerationProvider()
        
        topic = "Machine Learning Basics"
        niche = "Tech Education"
        
        print("\n[Test 1] generate_title()")
        title = provider.generate_title(topic, niche)
        print(f"Result:\n{title}")
        if not title or not isinstance(title, str) or not title.strip():
            raise AssertionError("Title is empty or invalid.")
        print("  -> PASS: Generated valid non-empty string.")

        print("\n[Test 2] generate_description()")
        description = provider.generate_description(topic, title, niche)
        print(f"Result:\n{description}")
        if not description or not isinstance(description, str) or not description.strip():
            raise AssertionError("Description is empty or invalid.")
        print("  -> PASS: Generated valid non-empty string.")

        print("\n[Test 3] generate_script()")
        script = provider.generate_script(topic, title, niche)
        print(f"Result:\n{script}")
        if not script or not isinstance(script, str) or not script.strip():
            raise AssertionError("Script is empty or invalid.")
        print("  -> PASS: Generated valid non-empty string.")

        print("\n[Test 4] generate_hashtags()")
        hashtags = provider.generate_hashtags(topic, title, niche)
        print(f"Result: {hashtags}")
        if not hashtags or not isinstance(hashtags, list) or len(hashtags) == 0:
            raise AssertionError("Hashtags list is empty or invalid.")
        for tag in hashtags:
            if not isinstance(tag, str) or not tag.strip():
                raise AssertionError(f"Found empty or invalid hashtag in list: {hashtags}")
        print("  -> PASS: Generated valid list of string hashtags.")

    except Exception:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        sys.exit(1)
        
    print("\n--- All tests passed! Real Gemini API works as expected. ---")

if __name__ == "__main__":
    run_tests()
