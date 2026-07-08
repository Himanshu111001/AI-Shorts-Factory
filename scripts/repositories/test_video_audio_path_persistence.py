import os
import sys
import uuid
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.database import engine
from backend.models.base import Base
from backend.config.session import SessionLocal
from backend.repositories.channel_repository import ChannelRepository
from backend.repositories.video_repository import VideoRepository
from backend.models.enums.video_status import VideoStatus

def run_tests():
    print("--- Starting Video Audio Path Persistence Verification ---")
    
    db = SessionLocal()
    channel_repo = ChannelRepository(db)
    video_repo = VideoRepository(db)
    
    test_channel = None
    test_video = None
    
    try:
        print("\n[Setup] Creating temporary channel...")
        test_channel = channel_repo.create({
            "name": f"Audio Persistence Test Channel {uuid.uuid4().hex[:8]}",
            "niche": "Testing",
            "youtube_account": f"test_{uuid.uuid4().hex[:8]}",
            "is_active": True
        })
        
        print("\n[Test 1] Create Video")
        test_video = video_repo.create({
            "channel_id": test_channel.id,
            "topic": "Testing audio_path persistence"
        })
        
        print("\n[Test 2] Assert initial audio_path is None")
        if test_video.audio_path is not None:
            raise AssertionError("Initial audio_path must be None")
            
        print("\n[Test 3] Update audio_path via repository")
        test_path = "./storage/test/video/narration.fake"
        updated_video = video_repo.update(test_video.id, {"audio_path": test_path})
        
        if updated_video.audio_path != test_path:
            raise AssertionError(f"Expected '{test_path}', got '{updated_video.audio_path}'")
            
        print("\n[Test 4] Verify database persistence across sessions")
        db.expire_all()
        
        refetched_video = video_repo.get_by_id(test_video.id)
        if not refetched_video:
            raise AssertionError("Failed to refetch video")
            
        if refetched_video.audio_path != test_path:
            raise AssertionError(f"Persisted audio_path mismatch. Expected '{test_path}', got '{refetched_video.audio_path}'")
            
    except Exception:
        print("\n--- UNEXPECTED ERROR ---")
        traceback.print_exc()
        raise
        
    finally:
        print("\n[Cleanup] Removing temporary database records...")
        if test_video:
            try:
                video_repo.delete(test_video.id)
            except Exception:
                pass
        if test_channel:
            try:
                channel_repo.delete(test_channel.id)
            except Exception:
                pass
        db.close()
        
    print("\n--- All tests passed! Audio path persistence works as expected. ---")

if __name__ == "__main__":
    run_tests()
