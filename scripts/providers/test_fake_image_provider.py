import sys
import os
import tempfile
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.providers.image.base import ImageGenerationProvider
from backend.providers.image.fake import FakeImageGenerationProvider
from backend.providers.image.factory import ImageProviderFactory

def run_tests():
    print("--- Starting Fake Image Provider Tests ---")
    
    test_dir = tempfile.mkdtemp(prefix="aimf_fake_image_test_")
    
    try:
        # Test 1
        print("\n[Test 1] Verify inheritance")
        provider = FakeImageGenerationProvider()
        if not isinstance(provider, ImageGenerationProvider):
            raise AssertionError("Fake provider does not inherit from ImageGenerationProvider")
            
        # Test 2 & 3
        print("\n[Test 2 & 3] Valid generation & Filename ordering")
        prompts1 = ["A futuristic city at sunset", "A cyberpunk street", "A flying car"]
        output_dir1 = os.path.join(test_dir, "test2")
        paths1 = provider.generate_images(prompts1, output_dir1)
        
        if len(paths1) != 3: raise AssertionError("Count mismatch")
        expected_paths1 = [
            os.path.join(output_dir1, "image_001.fake"),
            os.path.join(output_dir1, "image_002.fake"),
            os.path.join(output_dir1, "image_003.fake")
        ]
        if paths1 != expected_paths1: raise AssertionError(f"Path mismatch. Expected {expected_paths1}, Got {paths1}")
        
        for p in paths1:
            if not os.path.exists(p): raise AssertionError(f"File missing: {p}")
            
        # Test 4
        print("\n[Test 4] Exact artifact content")
        for i, p in enumerate(paths1, 1):
            with open(p, "r", encoding="utf-8") as f:
                content = f.read()
            expected = f"FAKE_IMAGE_ARTIFACT\nINDEX:{i}\nTOTAL:3\nPROMPT:{prompts1[i-1].strip()}"
            if content != expected:
                raise AssertionError(f"Content mismatch in {p}. Expected:\n{expected}\nGot:\n{content}")
                
        # Test 5
        print("\n[Test 5] Determinism")
        output_dir2 = os.path.join(test_dir, "test5")
        paths2 = provider.generate_images(prompts1, output_dir2)
        # Content in output_dir2 should match logic exactly
        for i, p in enumerate(paths2, 1):
            with open(p, "r", encoding="utf-8") as f:
                content2 = f.read()
            expected2 = f"FAKE_IMAGE_ARTIFACT\nINDEX:{i}\nTOTAL:3\nPROMPT:{prompts1[i-1].strip()}"
            if content2 != expected2:
                raise AssertionError("Determinism failed")
                
        # Test 6
        print("\n[Test 6] Different prompt")
        prompts2 = ["A cyberpunk street"]
        output_dir3 = os.path.join(test_dir, "test6")
        paths3 = provider.generate_images(prompts2, output_dir3)
        with open(paths3[0], "r", encoding="utf-8") as f:
            content3 = f.read()
        expected3 = f"FAKE_IMAGE_ARTIFACT\nINDEX:1\nTOTAL:1\nPROMPT:{prompts2[0]}"
        if content3 != expected3: raise AssertionError("Different prompt failed")

        # Test 7
        print("\n[Test 7] Empty prompt rejection")
        try:
            provider.generate_images([], test_dir)
            raise AssertionError("Should reject empty prompts list")
        except ValueError as e:
            if "empty" not in str(e).lower(): raise AssertionError("Wrong error message")
            
        # Test 8
        print("\n[Test 8] Whitespace prompt rejection")
        try:
            provider.generate_images(["   \n \t"], test_dir)
            raise AssertionError("Should reject whitespace prompt")
        except ValueError as e:
            if "whitespace" not in str(e).lower(): raise AssertionError("Wrong error message")
            
        # Test 9 and 10 were about count which is removed, let's just keep factory tests
        print("\n[Test 11] Factory exact name")
        prov = ImageProviderFactory.create("fake")
        if not isinstance(prov, FakeImageGenerationProvider): raise AssertionError("Wrong provider")
        
        # Test 12
        print("\n[Test 12] Factory normalization")
        prov_norm = ImageProviderFactory.create("  FaKe  ")
        if not isinstance(prov_norm, FakeImageGenerationProvider): raise AssertionError("Normalization failed")
        
        # Test 13
        print("\n[Test 13] Unsupported provider rejection")
        try:
            ImageProviderFactory.create("openai")
            raise AssertionError("Allowed unsupported")
        except ValueError as e:
            if "Unsupported image generation provider: openai" not in str(e):
                raise AssertionError(f"Wrong error: {e}")
                
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)
        
    print("\n--- All Fake Image Provider Tests Passed ---")

if __name__ == "__main__":
    run_tests()
