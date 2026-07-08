import sys
import os
import traceback

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.providers.text.base import TextGenerationProvider
from backend.providers.text.fake import FakeTextGenerationProvider
from backend.providers.text.factory import TextProviderFactory

def run_tests():
    print("--- Starting TextProviderFactory Verification ---")
    
    try:
        # Test 1: Exact provider name
        print("\n[Test 1] Exact provider name ('fake')")
        provider1 = TextProviderFactory.create("fake")
        if not isinstance(provider1, TextGenerationProvider):
            raise AssertionError("provider1 does not inherit from TextGenerationProvider")
        if not isinstance(provider1, FakeTextGenerationProvider):
            raise AssertionError("provider1 is not an instance of FakeTextGenerationProvider")
        print("  -> PASS")

        # Test 2: Normalization with whitespace and mixed casing
        print("\n[Test 2] Normalization with whitespace and mixed casing ('  FaKe ')")
        provider2 = TextProviderFactory.create("  FaKe ")
        if not isinstance(provider2, FakeTextGenerationProvider):
            raise AssertionError("provider2 is not an instance of FakeTextGenerationProvider")
        print("  -> PASS")

        # Test 3: Unsupported provider name
        print("\n[Test 3] Unsupported provider name ('openai')")
        try:
            TextProviderFactory.create("openai")
            raise AssertionError("Allowed creation of unsupported provider 'openai'")
        except ValueError as e:
            expected_msg = "Unsupported text generation provider: openai"
            if str(e) != expected_msg:
                raise AssertionError(f"Expected message '{expected_msg}', got '{e}'")
            print("  -> PASS")

        # Test 4: Unsupported provider name with surrounding whitespace
        print("\n[Test 4] Unsupported provider name with surrounding whitespace ('  openai  ')")
        try:
            TextProviderFactory.create("  openai  ")
            raise AssertionError("Allowed creation of unsupported provider '  openai  '")
        except ValueError as e:
            expected_msg = "Unsupported text generation provider:   openai  "
            if str(e) != expected_msg:
                raise AssertionError(f"Expected message '{expected_msg}', got '{e}'")
            print("  -> PASS")

    except Exception as e:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        raise
        
    print("\n--- All tests passed! TextProviderFactory works as expected. ---")

if __name__ == "__main__":
    run_tests()
