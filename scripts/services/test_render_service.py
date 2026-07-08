import sys
import os
import uuid
import tempfile
import shutil
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.database import engine
from backend.models.base import Base
from backend.config.session import SessionLocal
from backend.repositories.channel_repository import ChannelRepository
from backend.repositories.video_repository import VideoRepository
from backend.repositories.generated_image_repository import GeneratedImageRepository
from backend.services.render_service import RenderService
from backend.providers.render.fake import FakeRenderProvider
from backend.providers.render.base import RenderProvider
from backend.config.settings import get_settings
from backend.services.dependency import get_render_service

class FailingRenderProvider(RenderProvider):
    def render_video(self, audio_path, image_paths, output_path):
        raise ValueError("Simulated render failure")

class RecordingRenderProvider(RenderProvider):
    def __init__(self, return_path):
        self.return_path = return_path
        self.last_audio_path = None
        self.last_image_paths = None
        self.last_output_path = None
        
    def render_video(self, audio_path, image_paths, output_path):
        self.last_audio_path = audio_path
        self.last_image_paths = image_paths
        self.last_output_path = output_path
        return self.return_path

class InvalidRenderProvider(RenderProvider):
    def render_video(self, audio_path, image_paths, output_path):
        return "   "

class InvalidNoneRenderProvider(RenderProvider):
    def render_video(self, audio_path, image_paths, output_path):
        return None

def run_tests():
    print("--- Starting RenderService Integration Tests ---")
    
    Base.metadata.create_all(bind=engine)
    
    original_storage_path = os.environ.get("STORAGE_PATH")
    test_storage_dir = tempfile.mkdtemp(prefix="aimf_render_service_")
    
    # Force settings reset and setup temporary storage
    os.environ["STORAGE_PATH"] = test_storage_dir
    get_settings.cache_clear()
    
    db = SessionLocal()
    channel_repo = ChannelRepository(db)
    video_repo = VideoRepository(db)
    image_repo = GeneratedImageRepository(db)
    fake_provider = FakeRenderProvider()
    service = RenderService(db, fake_provider)
    
    test_channel = None
    videos_created = []
    
    def create_video_fixture(audio_path="test.audio", setup_images=True):
        vid = video_repo.create({
            "channel_id": test_channel.id,
            "topic": f"Render Test {uuid.uuid4().hex[:6]}",
            "audio_path": audio_path
        })
        videos_created.append(vid)
        
        if setup_images:
            image_repo.create_many([
                {"video_id": vid.id, "sequence_index": 1, "prompt": "p1", "file_path": "path1"},
                {"video_id": vid.id, "sequence_index": 2, "prompt": "p2", "file_path": "path2"},
                {"video_id": vid.id, "sequence_index": 3, "prompt": "p3", "file_path": "path3"}
            ])
            
        return vid

    try:
        print("\n[Setup] Creating test channel...")
        test_channel = channel_repo.create({
            "name": f"RS Test {uuid.uuid4().hex[:8]}",
            "niche": "Testing",
            "youtube_account": f"rs_test_{uuid.uuid4().hex[:8]}",
            "is_active": True
        })
        
        print("\n[Test 1] Successful Render")
        video1 = create_video_fixture("audio.fake", setup_images=True)
        updated_video1 = service.render_video(video1.id)
        if not updated_video1.rendered_video_path:
            raise AssertionError("rendered_video_path is empty")
        if str(video1.id) not in updated_video1.rendered_video_path:
            raise AssertionError("Video ID not in path")
        if not os.path.exists(updated_video1.rendered_video_path):
            raise AssertionError("Artifact does not exist physically")
            
        print("\n[Test 2] Exact Artifact Content")
        with open(updated_video1.rendered_video_path, "r", encoding="utf-8") as f:
            content = f.read()
        lines = content.splitlines()
        if "AUDIO_PATH:audio.fake" not in lines: raise AssertionError("Wrong audio path in artifact")
        if "IMAGE_COUNT:3" not in lines: raise AssertionError("Wrong image count in artifact")
        if "IMAGE_001:path1" not in lines: raise AssertionError("Wrong image 1 in artifact")
        if "IMAGE_002:path2" not in lines: raise AssertionError("Wrong image 2 in artifact")
        if "IMAGE_003:path3" not in lines: raise AssertionError("Wrong image 3 in artifact")
        
        print("\n[Test 3] Database Persistence")
        db.expire_all()
        persisted1 = video_repo.get_by_id(video1.id)
        if persisted1.rendered_video_path != updated_video1.rendered_video_path:
            raise AssertionError("Path not persisted to DB")
            
        print("\n[Test 4] Cross-session Persistence")
        db2 = SessionLocal()
        try:
            video_repo2 = VideoRepository(db2)
            persisted2 = video_repo2.get_by_id(video1.id)
            if persisted2.rendered_video_path != updated_video1.rendered_video_path:
                raise AssertionError("Cross-session mismatch")
        finally:
            db2.close()
            
        print("\n[Test 5] Missing Video")
        try:
            service.render_video(uuid.uuid4())
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            if str(e) != "Video not found": raise AssertionError(f"Wrong error: {e}")
            
        print("\n[Test 6] Missing Audio Path")
        video6 = create_video_fixture(audio_path=None, setup_images=True)
        try:
            service.render_video(video6.id)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            if str(e) != "Video rendering requires generated audio": raise AssertionError(f"Wrong error: {e}")
            
        print("\n[Test 7] Whitespace Audio Path")
        video7 = create_video_fixture(audio_path="   ", setup_images=True)
        try:
            service.render_video(video7.id)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            if str(e) != "Video rendering requires generated audio": raise AssertionError(f"Wrong error: {e}")
            
        print("\n[Test 8] No Generated Images")
        video8 = create_video_fixture("audio.fake", setup_images=False)
        try:
            service.render_video(video8.id)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            if str(e) != "Video rendering requires generated images": raise AssertionError(f"Wrong error: {e}")
            
        print("\n[Test 9] Invalid Generated Image Path")
        video9 = create_video_fixture("audio.fake", setup_images=False)
        image_repo.create({"video_id": video9.id, "sequence_index": 1, "prompt": "p1", "file_path": "   "})
        try:
            service.render_video(video9.id)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            if str(e) != "Generated image contains invalid file path": raise AssertionError(f"Wrong error: {e}")
            
        print("\n[Test 10] Missing Provider")
        none_service = RenderService(db, render_provider=None)
        try:
            none_service.render_video(video1.id)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            if str(e) != "Render provider is not configured": raise AssertionError(f"Wrong error: {e}")
            
        print("\n[Test 11] Provider Failure Safety")
        fail_service = RenderService(db, FailingRenderProvider())
        video11 = create_video_fixture("audio.fake", setup_images=True)
        old_path = "storage/old/final.fake"
        video_repo.update(video11.id, {"rendered_video_path": old_path})
        try:
            fail_service.render_video(video11.id)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            if str(e) != "Simulated render failure": raise AssertionError(f"Wrong error: {e}")
        db.expire_all()
        if video_repo.get_by_id(video11.id).rendered_video_path != old_path:
            raise AssertionError("Path was wiped by failure")
            
        print("\n[Test 12] Invalid Provider Result Safety")
        inv_service = RenderService(db, InvalidRenderProvider())
        video12 = create_video_fixture("audio.fake", setup_images=True)
        video_repo.update(video12.id, {"rendered_video_path": old_path})
        try:
            inv_service.render_video(video12.id)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            if str(e) != "Render provider returned invalid output path": raise AssertionError(f"Wrong error: {e}")
        db.expire_all()
        if video_repo.get_by_id(video12.id).rendered_video_path != old_path:
            raise AssertionError("Path was wiped by invalid result")
            
        inv_none_service = RenderService(db, InvalidNoneRenderProvider())
        video_repo.update(video12.id, {"rendered_video_path": old_path})
        try:
            inv_none_service.render_video(video12.id)
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            if str(e) != "Render provider returned invalid output path": raise AssertionError(f"Wrong error: {e}")
        db.expire_all()
        if video_repo.get_by_id(video12.id).rendered_video_path != old_path:
            raise AssertionError("Path was wiped by invalid none result")
            
        print("\n[Test 13] Successful Rerender")
        record_provider = RecordingRenderProvider("new/final.fake")
        rerender_service = RenderService(db, record_provider)
        video13 = create_video_fixture("audio.fake", setup_images=True)
        video_repo.update(video13.id, {"rendered_video_path": old_path})
        updated13 = rerender_service.render_video(video13.id)
        if updated13.rendered_video_path != "new/final.fake":
            raise AssertionError("Rerender did not update path")
            
        print("\n[Test 14] Image Ordering")
        video14 = create_video_fixture("audio.fake", setup_images=False)
        # Insert out of order
        image_repo.create({"video_id": video14.id, "sequence_index": 3, "prompt": "p3", "file_path": "path3"})
        image_repo.create({"video_id": video14.id, "sequence_index": 1, "prompt": "p1", "file_path": "path1"})
        image_repo.create({"video_id": video14.id, "sequence_index": 2, "prompt": "p2", "file_path": "path2"})
        
        ord_provider = RecordingRenderProvider("final")
        ord_service = RenderService(db, ord_provider)
        ord_service.render_video(video14.id)
        if ord_provider.last_image_paths != ["path1", "path2", "path3"]:
            raise AssertionError(f"Images passed to provider in wrong order: {ord_provider.last_image_paths}")
            
        print("\n[Test 15] Dependency Constructor Identity")
        dep_service = get_render_service(db, fake_provider)
        if not isinstance(dep_service, RenderService): raise AssertionError("Not RenderService")
        if dep_service.db is not db: raise AssertionError("DB mismatch")
        if dep_service.render_provider is not fake_provider: raise AssertionError("Provider mismatch")
        if dep_service.video_repo.db is not db: raise AssertionError("Video repo DB mismatch")
        if dep_service.image_repo.db is not db: raise AssertionError("Image repo DB mismatch")
        
        print("\n[Output Path Ownership Verification]")
        expected_req_path = os.path.join(str(Path(test_storage_dir) / "videos" / str(video14.id) / "final.fake"))
        # Using ord_provider from Test 14
        if ord_provider.last_output_path != expected_req_path:
            raise AssertionError(f"Expected path {expected_req_path}, got {ord_provider.last_output_path}")

    finally:
        print("\n[Cleanup] Removing temporary resources...")
        try:
            for vid in videos_created:
                image_repo.delete_by_video_id(vid.id)
                video_repo.delete(vid.id)
            if test_channel:
                channel_repo.delete(test_channel.id)
        except Exception as e:
            print(f"Cleanup error (ignorable): {e}")
        
        db.close()
        shutil.rmtree(test_storage_dir, ignore_errors=True)
        
        if original_storage_path is not None:
            os.environ["STORAGE_PATH"] = original_storage_path
        else:
            if "STORAGE_PATH" in os.environ:
                del os.environ["STORAGE_PATH"]
        get_settings.cache_clear()

    print("\n--- All RenderService Integration Tests Passed! ---")

if __name__ == "__main__":
    run_tests()
