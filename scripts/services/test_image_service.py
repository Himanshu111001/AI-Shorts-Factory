import sys
import os
import uuid
import traceback
from pathlib import Path
import shutil

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.database import engine
from backend.models.base import Base
from backend.config.session import SessionLocal
from backend.config.settings import get_settings
from backend.repositories.channel_repository import ChannelRepository
from backend.repositories.video_repository import VideoRepository
from backend.repositories.generated_image_repository import GeneratedImageRepository
from backend.providers.image.fake import FakeImageGenerationProvider
from backend.providers.image.base import ImageGenerationProvider
from backend.services.image_service import ImageService
from backend.services.dependency import get_image_service

class FailingImageProvider(ImageGenerationProvider):
    def generate_images(self, prompts, output_dir):
        raise RuntimeError("Test Provider Failed")

class InvalidResultImageProvider(ImageGenerationProvider):
    def __init__(self, mode="wrong_count"):
        self.mode = mode
    def generate_images(self, prompts, output_dir):
        if self.mode == "wrong_count":
            return ["/p1.png"]
        elif self.mode == "empty_path":
            paths = ["/path.png" for _ in prompts]
            paths[0] = "  "
            return paths
        elif self.mode == "not_list":
            return "not a list"
        return []

def run_tests():
    print("--- Starting ImageService Tests ---")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    settings = get_settings()
    
    channel_repo = ChannelRepository(db)
    video_repo = VideoRepository(db)
    img_repo = GeneratedImageRepository(db)
    
    fake_provider = FakeImageGenerationProvider()
    service = get_image_service(db, fake_provider)
    
    test_channel = None
    v1 = None
    v2 = None
    
    try:
        # TEST 15 - DEPENDENCY CONSTRUCTOR
        print("\n[Test 15] Dependency Constructor Identity")
        if not isinstance(service, ImageService): raise AssertionError("Not an ImageService")
        if service.db is not db: raise AssertionError("DB mismatch")
        if service.image_provider is not fake_provider: raise AssertionError("Provider mismatch")
        if service.video_repo.db is not db: raise AssertionError("Repo DB mismatch")
        if service.image_repo.db is not db: raise AssertionError("Repo DB mismatch")
        
        print("\n[Setup] Creating temporary Channel and Videos...")
        test_channel = channel_repo.create({
            "name": "Image Service Channel",
            "niche": "Testing",
            "youtube_account": f"test_{uuid.uuid4().hex[:8]}",
            "is_active": True
        })
        
        v1 = video_repo.create({"channel_id": test_channel.id, "topic": "V1"})
        v1.script = "Sentence one. Sentence two! Sentence three? Sentence four."
        db.commit()
        
        v2 = video_repo.create({"channel_id": test_channel.id, "topic": "V2"})
        v2.script = "One short sentence."
        db.commit()
        
        # TEST 1 - SUCCESSFUL IMAGE GENERATION
        print("\n[Test 1] Successful Image Generation")
        imgs = service.generate_images(v1.id, 4)
        if len(imgs) != 4: raise AssertionError(f"Expected 4 images, got {len(imgs)}")
        
        seqs = [img.sequence_index for img in imgs]
        if seqs != [1, 2, 3, 4]: raise AssertionError(f"Sequence mismatch: {seqs}")
        
        for img in imgs:
            if not img.prompt: raise AssertionError("Empty prompt")
            if not img.file_path: raise AssertionError("Empty file path")
            if not os.path.exists(img.file_path): raise AssertionError(f"File missing: {img.file_path}")
            
        # TEST 2 - EXACT PROMPT PERSISTENCE
        print("\n[Test 2] Exact Prompt Persistence")
        for img in imgs:
            with open(img.file_path, "r", encoding="utf-8") as f:
                content = f.read()
            if img.prompt.strip() not in content:
                raise AssertionError(f"Prompt {img.prompt} not found in fake artifact content:\n{content}")
                
        # TEST 3 - DATABASE PERSISTENCE
        print("\n[Test 3] Database Persistence")
        db.expire_all()
        fetched = img_repo.get_by_video_id(v1.id)
        if len(fetched) != 4: raise AssertionError("Fetch count mismatch")
        if [i.sequence_index for i in fetched] != [1, 2, 3, 4]: raise AssertionError("Fetch order mismatch")
        if fetched[0].prompt != imgs[0].prompt: raise AssertionError("Prompt mismatch")
        if fetched[0].file_path != imgs[0].file_path: raise AssertionError("Filepath mismatch")
        
        # TEST 4 - DETERMINISTIC PLANNING
        print("\n[Test 4] Deterministic Planning")
        p1 = service._plan_scene_prompts("Hello world. Testing this.", 2)
        p2 = service._plan_scene_prompts("Hello world. Testing this.", 2)
        if p1 != p2: raise AssertionError("Deterministic planning failed")
        
        p3 = service._plan_scene_prompts("Different script. Entirely new.", 2)
        if p1 == p3: raise AssertionError("Different script returned same prompts")
        
        # TEST 5 - FEWER SENTENCES THAN IMAGE COUNT
        print("\n[Test 5] Fewer Sentences Than Image Count")
        v2_imgs = service.generate_images(v2.id, 4)
        if len(v2_imgs) != 4: raise AssertionError("Fallback failed to return 4 images")
        for i in v2_imgs:
            if not i.prompt: raise AssertionError("Empty prompt in fallback")
            
        # TEST 6 - MISSING VIDEO
        print("\n[Test 6] Missing Video")
        try:
            service.generate_images(uuid.uuid4(), 4)
            raise AssertionError("Allowed missing video")
        except ValueError as e:
            if "Video not found" not in str(e): raise AssertionError("Wrong error msg")
            
        # TEST 7 & 8 - MISSING / WHITESPACE SCRIPT
        print("\n[Test 7 & 8] Missing / Whitespace Script")
        v_no_script = video_repo.create({"channel_id": test_channel.id, "topic": "V3"})
        try:
            service.generate_images(v_no_script.id, 4)
            raise AssertionError("Allowed missing script")
        except ValueError as e:
            if "requires generated script" not in str(e): raise AssertionError("Wrong error msg")
            
        v_no_script.script = "   \n "
        db.commit()
        try:
            service.generate_images(v_no_script.id, 4)
            raise AssertionError("Allowed whitespace script")
        except ValueError as e:
            if "requires generated script" not in str(e): raise AssertionError("Wrong error msg")
            
        # TEST 9 - MISSING PROVIDER
        print("\n[Test 9] Missing Provider")
        bad_service = ImageService(db, None)
        try:
            bad_service.generate_images(v1.id, 4)
            raise AssertionError("Allowed missing provider")
        except ValueError as e:
            if "not configured" not in str(e): raise AssertionError("Wrong error msg")
            
        # TEST 10 - INVALID IMAGE COUNT
        print("\n[Test 10] Invalid Image Count")
        try:
            service.generate_images(v1.id, 0)
            raise AssertionError("Allowed count=0")
        except ValueError as e:
            if "greater than 0" not in str(e): raise AssertionError("Wrong error msg")
            
        # TEST 11 - PROVIDER FAILURE SAFETY
        print("\n[Test 11] Provider Failure Safety")
        fail_service = ImageService(db, FailingImageProvider())
        old_ids = [i.id for i in img_repo.get_by_video_id(v1.id)]
        try:
            fail_service.generate_images(v1.id, 4)
            raise AssertionError("Allowed failing provider")
        except RuntimeError:
            pass
        new_ids = [i.id for i in img_repo.get_by_video_id(v1.id)]
        if old_ids != new_ids: raise AssertionError("Safety failed on provider exception")
        
        # TEST 12 - INVALID PROVIDER RESULT SAFETY
        print("\n[Test 12] Invalid Provider Result Safety")
        for mode in ["wrong_count", "empty_path", "not_list"]:
            inv_service = ImageService(db, InvalidResultImageProvider(mode=mode))
            try:
                inv_service.generate_images(v1.id, 4)
                raise AssertionError(f"Allowed invalid result mode: {mode}")
            except ValueError as e:
                if "invalid result" not in str(e): raise AssertionError("Wrong error msg")
            
            check_ids = [i.id for i in img_repo.get_by_video_id(v1.id)]
            if old_ids != check_ids: raise AssertionError(f"Safety failed on invalid result mode: {mode}")
            
        # TEST 13 - SUCCESSFUL REGENERATION
        print("\n[Test 13] Successful Regeneration")
        v1.script = "A brand new. Completely different. Set of sentences. For sure."
        db.commit()
        regen_imgs = service.generate_images(v1.id, 4)
        if len(regen_imgs) != 4: raise AssertionError("Regen failed")
        regen_ids = [i.id for i in regen_imgs]
        if set(old_ids).intersection(set(regen_ids)): raise AssertionError("Old IDs were reused or not deleted")
        if regen_imgs[0].prompt == imgs[0].prompt: raise AssertionError("Prompts did not change")
        
    except Exception:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        print("\n[Cleanup] Removing temporary database records and storage...")
        if v1: 
            img_repo.delete_by_video_id(v1.id)
            d = Path(settings.storage_path) / "videos" / str(v1.id)
            shutil.rmtree(d, ignore_errors=True)
            try: video_repo.delete(v1.id)
            except Exception: pass
            
        if v2: 
            img_repo.delete_by_video_id(v2.id)
            d = Path(settings.storage_path) / "videos" / str(v2.id)
            shutil.rmtree(d, ignore_errors=True)
            try: video_repo.delete(v2.id)
            except Exception: pass
            
        try: video_repo.delete_by_channel(test_channel.id)
        except Exception: pass
            
        if test_channel:
            try: channel_repo.delete(test_channel.id)
            except Exception: pass
            
        db.close()
        
    print("\n--- All ImageService Tests Passed ---")

if __name__ == "__main__":
    run_tests()
