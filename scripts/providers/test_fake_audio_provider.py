import sys
import os
import shutil
import tempfile
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.providers.audio.base import AudioGenerationProvider
from backend.providers.audio.fake import FakeAudioGenerationProvider
from backend.providers.audio.factory import AudioProviderFactory

def run_tests():
    print("--- Starting Fake Audio Provider Tests ---")
    
    test_dir = tempfile.mkdtemp(prefix="aimf_test_audio_")
    
    try:
        # Test 1: Inheritance
        print("\n[Test 1] Inheritance Check")
        provider = FakeAudioGenerationProvider()
        if not isinstance(provider, AudioGenerationProvider):
            raise AssertionError("FakeAudioGenerationProvider must inherit from AudioGenerationProvider")
            
        # Test 2: Valid generation
        print("\n[Test 2] Valid Generation")
        out1 = os.path.join(test_dir, "deep", "path", "audio1.wav")
        res1 = provider.generate_audio("Hello world", out1)
        if res1 != out1: raise AssertionError("Returned path does not match requested path")
        if not os.path.exists(out1): raise AssertionError("File was not created")
        
        # Test 3: Determinism
        print("\n[Test 3] Determinism")
        out2 = os.path.join(test_dir, "audio2.wav")
        provider.generate_audio("Hello world", out2)
        with open(out1, "r", encoding="utf-8") as f1, open(out2, "r", encoding="utf-8") as f2:
            if f1.read() != f2.read():
                raise AssertionError("Artifact contents are not deterministic for the same input")
                
        # Test 4: Different input
        print("\n[Test 4] Different input")
        out3 = os.path.join(test_dir, "audio3.wav")
        provider.generate_audio("Different text", out3)
        with open(out1, "r", encoding="utf-8") as f1, open(out3, "r", encoding="utf-8") as f3:
            if f1.read() == f3.read():
                raise AssertionError("Artifact contents must differ for different input texts")
                
        # Test 5: Empty input rejection
        print("\n[Test 5] Empty input rejection")
        try:
            provider.generate_audio("", os.path.join(test_dir, "empty.wav"))
            raise AssertionError("Did not reject empty string")
        except ValueError:
            pass
            
        try:
            provider.generate_audio("   ", os.path.join(test_dir, "spaces.wav"))
            raise AssertionError("Did not reject whitespace string")
        except ValueError:
            pass

        # Test 6: Factory exact name
        print("\n[Test 6] Factory exact name")
        fact_prov1 = AudioProviderFactory.create("fake")
        if not isinstance(fact_prov1, FakeAudioGenerationProvider):
            raise AssertionError("Factory did not return FakeAudioGenerationProvider for 'fake'")
            
        # Test 7: Factory normalization
        print("\n[Test 7] Factory normalization")
        fact_prov2 = AudioProviderFactory.create("  FaKe  ")
        if not isinstance(fact_prov2, FakeAudioGenerationProvider):
            raise AssertionError("Factory did not return FakeAudioGenerationProvider for '  FaKe  '")
            
        # Test 8: Unsupported provider
        print("\n[Test 8] Unsupported provider")
        try:
            AudioProviderFactory.create("elevenlabs")
            raise AssertionError("Did not reject 'elevenlabs'")
        except ValueError as e:
            if str(e) != "Unsupported audio generation provider: elevenlabs":
                raise AssertionError(f"Wrong error message: {str(e)}")
                
    except Exception:
        print("\n--- UNEXPECTED ERROR ---")
        traceback.print_exc()
        sys.exit(1)
    finally:
        print("\n[Cleanup] Removing temporary test directory...")
        shutil.rmtree(test_dir, ignore_errors=True)
        
    print("\n--- All Fake Audio Provider tests passed! ---")

if __name__ == "__main__":
    run_tests()
