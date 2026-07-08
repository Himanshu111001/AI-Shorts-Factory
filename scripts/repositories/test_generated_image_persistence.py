import sys
import os
import uuid
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.database import engine
from backend.models.base import Base
from backend.config.session import SessionLocal
from backend.repositories.channel_repository import ChannelRepository
from backend.repositories.video_repository import VideoRepository
from backend.repositories.generated_image_repository import GeneratedImageRepository

def run_tests():
    print("--- Starting GeneratedImage Persistence Cross-Session Test ---")
    Base.metadata.create_all(bind=engine)
    
    # Session 1: Setup and Create
    db1 = SessionLocal()
    channel_repo = ChannelRepository(db1)
    video_repo = VideoRepository(db1)
    img_repo = GeneratedImageRepository(db1)
    
    test_channel_id = None
    v1_id = None
    
    try:
        print("\n[Session 1] Creating temporary Channel and Video...")
        test_channel = channel_repo.create({
            "name": "Persistence Test Channel",
            "niche": "Testing",
            "youtube_account": f"pers_{uuid.uuid4().hex[:8]}",
            "is_active": True
        })
        v1 = video_repo.create({"channel_id": test_channel.id, "topic": "Persistence V1"})
        
        print("[Session 1] Persisting 3 GeneratedImages...")
        img_repo.create_many([
            {"video_id": v1.id, "sequence_index": 1, "prompt": "Prompt1", "file_path": "/p1.png"},
            {"video_id": v1.id, "sequence_index": 2, "prompt": "Prompt2", "file_path": "/p2.png"},
            {"video_id": v1.id, "sequence_index": 3, "prompt": "Prompt3", "file_path": "/p3.png"}
        ])
        v1_id = v1.id
        test_channel_id = test_channel.id
    except Exception:
        print("Setup failed in session 1")
        db1.close()
        sys.exit(1)
        
    db1.close()
    
    # Session 2: Read and Verify
    db2 = SessionLocal()
    img_repo2 = GeneratedImageRepository(db2)
    video_repo2 = VideoRepository(db2)
    channel_repo2 = ChannelRepository(db2)
    
    try:
        print("\n[Session 2] Fetching by video_id...")
        fetched = img_repo2.get_by_video_id(v1_id)
        
        if len(fetched) != 3: raise AssertionError(f"Expected 3 rows, got {len(fetched)}")
        
        seqs = [img.sequence_index for img in fetched]
        if seqs != [1, 2, 3]: raise AssertionError(f"Ordering mismatch: {seqs}")
        
        if fetched[0].prompt != "Prompt1": raise AssertionError("Prompt mismatch")
        if fetched[1].prompt != "Prompt2": raise AssertionError("Prompt mismatch")
        if fetched[2].prompt != "Prompt3": raise AssertionError("Prompt mismatch")
        
        if fetched[0].file_path != "/p1.png": raise AssertionError("Filepath mismatch")
        if fetched[1].file_path != "/p2.png": raise AssertionError("Filepath mismatch")
        if fetched[2].file_path != "/p3.png": raise AssertionError("Filepath mismatch")
        
        for img in fetched:
            if img.id is None: raise AssertionError("ID is None")
            
    except Exception:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        print("\n[Cleanup] Removing temporary database records via Session 2...")
        if v1_id: img_repo2.delete_by_video_id(v1_id)
        if v1_id:
            try: video_repo2.delete(v1_id)
            except Exception: pass
        if test_channel_id:
            try: channel_repo2.delete(test_channel_id)
            except Exception: pass
            
        db2.close()
        
    print("\n--- All GeneratedImage Persistence Tests Passed ---")

if __name__ == "__main__":
    run_tests()
