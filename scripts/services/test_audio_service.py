import sys
import os
import uuid
import tempfile
import shutil
import traceback
from pathlib import Path

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.database import engine
from backend.models.base import Base
from backend.config.session import SessionLocal
from backend.repositories.channel_repository import ChannelRepository
from backend.repositories.video_repository import VideoRepository
from backend.services.audio_service import AudioService
from backend.providers.audio.fake import FakeAudioGenerationProvider
from backend.providers.audio.base import AudioGenerationProvider
from backend.config.settings import get_settings
from backend.services.dependency import get_audio_service
from backend.models.enums.video_status import VideoStatus

class FailingAudioProvider(AudioGenerationProvider):
    def generate_audio(self, text: str, output_path: str) -> str:
        raise ValueError("Simulated audio provider failure")

def run_integration_tests():
    print("--- Starting AudioService Integration Tests ---")
    
    # Setup test-specific storage path
    original_storage_path = os.environ.get("STORAGE_PATH")
    test_storage_dir = tempfile.mkdtemp(prefix="aimf_audio_test_")
    os.environ["STORAGE_PATH"] = test_storage_dir
    get_settings.cache_clear()
    
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    channel_repo = ChannelRepository(db)
    video_repo = VideoRepository(db)
    
    fake_provider = FakeAudioGenerationProvider()
    service = AudioService(db, audio_provider=fake_provider)
    
    test_channel = None
    created_video_ids = []
    
    try:
        print("\n[Setup] Creating temporary channel and videos...")
        test_channel = channel_repo.create({
            "name": f"AudioService Test Channel {uuid.uuid4().hex[:8]}",
            "niche": "AI Tech",
            "youtube_account": "integration_test_ai",
            "is_active": True
        })
        
        # Video 1: valid script
        video1 = video_repo.create({
            "channel_id": test_channel.id,
            "topic": "Test Audio Valid Script",
            "script": "This is a valid test script for audio generation."
        })
        created_video_ids.append(video1.id)
        
        # Test 1
        print("\n[Test 1] Successful audio generation")
        updated_video1 = service.generate_audio(video1.id)
        if updated_video1.id != video1.id: raise AssertionError("Returned wrong video ID")
        if updated_video1.audio_path is None: raise AssertionError("audio_path is None")
        
        # Verify path normalized semantics
        expected_path_suffix = os.path.join("videos", str(video1.id), "narration.fake")
        if expected_path_suffix not in updated_video1.audio_path:
            raise AssertionError(f"Expected path suffix {expected_path_suffix} not in {updated_video1.audio_path}")
        
        if not os.path.exists(updated_video1.audio_path):
            raise AssertionError("Artifact file does not exist")
            
        print("\n[Test 2] Artifact content verification")
        with open(updated_video1.audio_path, "r", encoding="utf-8") as f:
            content = f.read()
        expected_content = f"FAKE_AUDIO_ARTIFACT\nTEXT_LENGTH:{len(video1.script)}\nTEXT:{video1.script.strip()}"
        if content != expected_content:
            raise AssertionError(f"Artifact content mismatch.\nExpected: {expected_content}\nGot: {content}")
            
        print("\n[Test 3] Database persistence")
        original_status = updated_video1.status
        db.expire_all()
        refetched_video = video_repo.get_by_id(video1.id)
        if refetched_video.audio_path != updated_video1.audio_path:
            raise AssertionError("audio_path not persisted correctly")
        if refetched_video.script != video1.script:
            raise AssertionError("script was unexpectedly modified")
        if refetched_video.status != original_status:
            raise AssertionError("status was unexpectedly modified")
        if not os.path.exists(refetched_video.audio_path):
            raise AssertionError("Artifact file disappeared")
            
        print("\n[Test 4] Missing Video validation")
        random_id = uuid.uuid4()
        try:
            service.generate_audio(random_id)
            raise AssertionError("Did not reject missing video")
        except ValueError as e:
            if str(e) != "Video not found":
                raise AssertionError(f"Wrong error: {e}")
                
        print("\n[Test 5] Missing script validation")
        video_no_script = video_repo.create({
            "channel_id": test_channel.id,
            "topic": "No Script Video",
            "script": None
        })
        created_video_ids.append(video_no_script.id)
        try:
            service.generate_audio(video_no_script.id)
            raise AssertionError("Did not reject None script")
        except ValueError as e:
            if str(e) != "Audio generation requires generated script":
                raise AssertionError(f"Wrong error: {e}")
                
        db.expire_all()
        if video_repo.get_by_id(video_no_script.id).audio_path is not None:
            raise AssertionError("audio_path should remain None")

        print("\n[Test 6] Whitespace-only script validation")
        video_whitespace = video_repo.create({
            "channel_id": test_channel.id,
            "topic": "Whitespace Script Video",
            "script": "   \n  \t  "
        })
        created_video_ids.append(video_whitespace.id)
        try:
            service.generate_audio(video_whitespace.id)
            raise AssertionError("Did not reject whitespace script")
        except ValueError as e:
            if str(e) != "Audio generation requires generated script":
                raise AssertionError(f"Wrong error: {e}")
        db.expire_all()
        if video_repo.get_by_id(video_whitespace.id).audio_path is not None:
            raise AssertionError("audio_path should remain None")
            
        print("\n[Test 7] Missing provider validation")
        service_no_provider = AudioService(db, audio_provider=None)
        try:
            service_no_provider.generate_audio(video1.id)
            raise AssertionError("Did not reject missing provider")
        except ValueError as e:
            if str(e) != "Audio generation provider is not configured":
                raise AssertionError(f"Wrong error: {e}")
                
        print("\n[Test 8] Provider failure safety")
        failing_provider = FailingAudioProvider()
        service_failing = AudioService(db, audio_provider=failing_provider)
        video_failing = video_repo.create({
            "channel_id": test_channel.id,
            "topic": "Failing Provider Test",
            "script": "Test script",
            "status": VideoStatus.PROCESSING
        })
        created_video_ids.append(video_failing.id)
        try:
            service_failing.generate_audio(video_failing.id)
            raise AssertionError("Did not propagate provider error")
        except ValueError as e:
            if str(e) != "Simulated audio provider failure":
                raise AssertionError(f"Wrong error: {e}")
                
        db.expire_all()
        refetched_failing = video_repo.get_by_id(video_failing.id)
        if refetched_failing.audio_path is not None: raise AssertionError("audio_path should be None on failure")
        if refetched_failing.status != VideoStatus.PROCESSING: raise AssertionError("Status unexpectedly changed")
        if refetched_failing.script != "Test script": raise AssertionError("Script unexpectedly changed")
        
        print("\n[Test 9] Dependency constructor identity")
        constructed_service = get_audio_service(db=db, audio_provider=fake_provider)
        if not isinstance(constructed_service, AudioService): raise AssertionError("Not an AudioService")
        if constructed_service.db is not db: raise AssertionError("DB instance mismatch")
        if constructed_service.audio_provider is not fake_provider: raise AssertionError("Provider instance mismatch")
        if constructed_service.video_repo.db is not db: raise AssertionError("Video repo DB instance mismatch")
        
    except Exception as e:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        raise
        
    finally:
        print("\n[Cleanup] Removing temporary database records and audio artifacts...")
        for vid in created_video_ids:
            try:
                video_repo.delete(vid)
            except Exception:
                pass
        if test_channel:
            try:
                channel_repo.delete(test_channel.id)
            except Exception:
                pass
                
        db.close()
        
        shutil.rmtree(test_storage_dir, ignore_errors=True)
        
        if original_storage_path is not None:
            os.environ["STORAGE_PATH"] = original_storage_path
        else:
            if "STORAGE_PATH" in os.environ:
                del os.environ["STORAGE_PATH"]
        get_settings.cache_clear()
        
    print("\n--- All tests passed! AudioService works as expected. ---")

if __name__ == "__main__":
    run_integration_tests()
