import sys
import os
import tempfile
import shutil
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.providers.render.base import RenderProvider
from backend.providers.render.fake import FakeRenderProvider
from backend.providers.render.factory import RenderProviderFactory

def run_tests():
    print("--- Starting Fake Render Provider Tests ---")
    
    test_dir = tempfile.mkdtemp(prefix="aimf_test_render_")
    
    try:
        print("\n[Test 1] Inheritance")
        provider = FakeRenderProvider()
        if not isinstance(provider, RenderProvider):
            raise AssertionError("FakeRenderProvider is not a RenderProvider")
            
        print("\n[Test 2] Valid Render")
        out_path = os.path.join(test_dir, "final.fake")
        ret_path = provider.render_video(
            audio_path="audio/narration.fake",
            image_paths=[
                "images/image_001.fake",
                "images/image_002.fake",
                "images/image_003.fake",
            ],
            output_path=out_path
        )
        if ret_path != out_path: raise AssertionError(f"Expected {out_path}, got {ret_path}")
        if not os.path.exists(out_path): raise AssertionError("Output artifact not created")
        if not os.path.isfile(out_path): raise AssertionError("Output artifact is not a file")
        with open(out_path, "r", encoding="utf-8") as f:
            content = f.read()
        if not content.strip(): raise AssertionError("Artifact content is empty")
        
        print("\n[Test 3] Exact Artifact Content")
        lines = content.split("\n")
        if lines[0] != "FAKE_RENDER_ARTIFACT": raise AssertionError("Wrong header")
        if lines[1] != "AUDIO_PATH:audio/narration.fake": raise AssertionError("Wrong audio path")
        if lines[2] != "IMAGE_COUNT:3": raise AssertionError("Wrong image count")
        if lines[3] != "IMAGE_001:images/image_001.fake": raise AssertionError("Wrong image 1")
        if lines[4] != "IMAGE_002:images/image_002.fake": raise AssertionError("Wrong image 2")
        if lines[5] != "IMAGE_003:images/image_003.fake": raise AssertionError("Wrong image 3")
        
        print("\n[Test 4] Determinism")
        out_path2 = os.path.join(test_dir, "final2.fake")
        provider.render_video(
            audio_path="audio/narration.fake",
            image_paths=["images/image_001.fake", "images/image_002.fake", "images/image_003.fake"],
            output_path=out_path2
        )
        with open(out_path2, "r", encoding="utf-8") as f:
            content2 = f.read()
        if content != content2: raise AssertionError("Renders with identical inputs are not equal")
        
        print("\n[Test 5] Image Order Sensitivity")
        out_path3 = os.path.join(test_dir, "final3.fake")
        provider.render_video(
            audio_path="audio/narration.fake",
            image_paths=["images/image_003.fake", "images/image_002.fake", "images/image_001.fake"],
            output_path=out_path3
        )
        with open(out_path3, "r", encoding="utf-8") as f:
            content3 = f.read()
        if content == content3: raise AssertionError("Renders with different image order are equal")
        
        print("\n[Test 6] Audio Path Sensitivity")
        out_path4 = os.path.join(test_dir, "final4.fake")
        provider.render_video(
            audio_path="audio/other_narration.fake",
            image_paths=["images/image_001.fake", "images/image_002.fake", "images/image_003.fake"],
            output_path=out_path4
        )
        with open(out_path4, "r", encoding="utf-8") as f:
            content4 = f.read()
        if content == content4: raise AssertionError("Renders with different audio path are equal")
        
        print("\n[Test 7] Empty Audio Path")
        try:
            provider.render_video("", ["img1"], os.path.join(test_dir, "t7.fake"))
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            if str(e) != "Audio path is required": raise AssertionError(f"Wrong error: {e}")
            
        print("\n[Test 8] Empty Image List")
        try:
            provider.render_video("audio", [], os.path.join(test_dir, "t8.fake"))
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            if str(e) != "At least one image path is required": raise AssertionError(f"Wrong error: {e}")
            
        print("\n[Test 9] Invalid Image Path Entry")
        try:
            provider.render_video("audio", ["img1", ""], os.path.join(test_dir, "t9a.fake"))
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            if str(e) != "Image paths must contain non-empty strings": raise AssertionError(f"Wrong error: {e}")
        try:
            provider.render_video("audio", ["img1", "   "], os.path.join(test_dir, "t9b.fake"))
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            if str(e) != "Image paths must contain non-empty strings": raise AssertionError(f"Wrong error: {e}")
            
        print("\n[Test 10] Empty Output Path")
        try:
            provider.render_video("audio", ["img1"], "   ")
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            if str(e) != "Output path is required": raise AssertionError(f"Wrong error: {e}")
            
        print("\n[Test 11] Factory Exact Name")
        fact_prov = RenderProviderFactory.create("fake")
        if not isinstance(fact_prov, FakeRenderProvider): raise AssertionError("Factory failed for 'fake'")
        
        print("\n[Test 12] Factory Normalization")
        fact_prov2 = RenderProviderFactory.create("  FaKe  ")
        if not isinstance(fact_prov2, FakeRenderProvider): raise AssertionError("Factory failed for '  FaKe  '")
        
        print("\n[Test 13] Unsupported Provider")
        try:
            RenderProviderFactory.create("ffmpeg")
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            if str(e) != "Unsupported render provider: ffmpeg": raise AssertionError(f"Wrong error: {e}")
            
    finally:
        shutil.rmtree(test_dir, ignore_errors=True)
        
    print("\n--- All Fake Render Provider Tests Passed! ---")

if __name__ == "__main__":
    run_tests()
