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
from sqlalchemy.exc import IntegrityError

def run_tests():
    print("--- Starting GeneratedImageRepository Tests ---")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    channel_repo = ChannelRepository(db)
    video_repo = VideoRepository(db)
    img_repo = GeneratedImageRepository(db)
    
    test_channel = None
    v1 = None
    v2 = None
    v3 = None
    
    try:
        print("\n[Setup] Creating temporary Channel and Videos...")
        test_channel = channel_repo.create({
            "name": "Image Repo Test Channel",
            "niche": "Testing",
            "youtube_account": f"test_{uuid.uuid4().hex[:8]}",
            "is_active": True
        })
        v1 = video_repo.create({"channel_id": test_channel.id, "topic": "V1"})
        v2 = video_repo.create({"channel_id": test_channel.id, "topic": "V2"})
        v3 = video_repo.create({"channel_id": test_channel.id, "topic": "V3"})
        
        # TEST 1 - SINGLE CREATE
        print("\n[Test 1] Single Create")
        img1 = img_repo.create({
            "video_id": v1.id,
            "sequence_index": 1,
            "prompt": "Test prompt 1",
            "file_path": "/test/1.fake"
        })
        if img1.id is None: raise AssertionError("ID is None")
        if img1.video_id != v1.id: raise AssertionError("video_id mismatch")
        if img1.sequence_index != 1: raise AssertionError("sequence_index mismatch")
        if img1.prompt != "Test prompt 1": raise AssertionError("prompt mismatch")
        if img1.file_path != "/test/1.fake": raise AssertionError("file_path mismatch")
        if img1.created_at is None: raise AssertionError("created_at is None")
        
        # TEST 2 - GET BY ID
        print("\n[Test 2] Get By ID")
        fetched1 = img_repo.get_by_id(img1.id)
        if fetched1 is None: raise AssertionError("Failed to get by ID")
        if fetched1.id != img1.id: raise AssertionError("ID mismatch on fetch")
        
        # TEST 3 - CREATE MANY
        print("\n[Test 3] Create Many")
        batch = [
            {"video_id": v1.id, "sequence_index": 2, "prompt": "P2", "file_path": "/test/2.fake"},
            {"video_id": v1.id, "sequence_index": 3, "prompt": "P3", "file_path": "/test/3.fake"},
            {"video_id": v1.id, "sequence_index": 4, "prompt": "P4", "file_path": "/test/4.fake"}
        ]
        created_imgs = img_repo.create_many(batch)
        if len(created_imgs) != 3: raise AssertionError("Did not return exactly 3 images")
        seqs = [img.sequence_index for img in created_imgs]
        if seqs != [2, 3, 4]: raise AssertionError(f"Sequence indexes mismatch: {seqs}")
        
        # TEST 4 - GET BY VIDEO ORDERING
        print("\n[Test 4] Get By Video Ordering")
        v1_imgs = img_repo.get_by_video_id(v1.id)
        v1_seqs = [img.sequence_index for img in v1_imgs]
        if v1_seqs != [1, 2, 3, 4]: raise AssertionError(f"Ordering mismatch: {v1_seqs}")
        
        # TEST 5 - DIFFERENT VIDEO ISOLATION
        print("\n[Test 5] Different Video Isolation")
        img_repo.create_many([
            {"video_id": v2.id, "sequence_index": 1, "prompt": "V2P1", "file_path": "/v2/1"},
            {"video_id": v2.id, "sequence_index": 2, "prompt": "V2P2", "file_path": "/v2/2"}
        ])
        v1_fetch = img_repo.get_by_video_id(v1.id)
        if len(v1_fetch) != 4: raise AssertionError("V1 count mismatch")
        v2_fetch = img_repo.get_by_video_id(v2.id)
        if len(v2_fetch) != 2: raise AssertionError("V2 count mismatch")
        
        # TEST 6 - DUPLICATE SEQUENCE CONSTRAINT
        print("\n[Test 6] Duplicate Sequence Constraint")
        try:
            img_repo.create({
                "video_id": v1.id,
                "sequence_index": 1,
                "prompt": "Dup",
                "file_path": "/dup"
            })
            raise AssertionError("Duplicate sequence allowed")
        except IntegrityError:
            pass
            
        # TEST 7 - INVALID ZERO SEQUENCE
        print("\n[Test 7] Invalid Zero Sequence")
        try:
            img_repo.create({
                "video_id": v1.id,
                "sequence_index": 0,
                "prompt": "Zero",
                "file_path": "/zero"
            })
            raise AssertionError("Zero sequence allowed")
        except IntegrityError:
            pass
            
        # TEST 8 - CREATE_MANY ATOMICITY
        print("\n[Test 8] Create_many Atomicity")
        bad_batch = [
            {"video_id": v3.id, "sequence_index": 1, "prompt": "P1", "file_path": "/v3/1"},
            {"video_id": v3.id, "sequence_index": 2, "prompt": "P2", "file_path": "/v3/2"},
            {"video_id": v3.id, "sequence_index": 2, "prompt": "DupP2", "file_path": "/v3/2_dup"},
            {"video_id": v3.id, "sequence_index": 3, "prompt": "P3", "file_path": "/v3/3"}
        ]
        try:
            img_repo.create_many(bad_batch)
            raise AssertionError("Bad batch allowed")
        except IntegrityError:
            pass
            
        v3_imgs = img_repo.get_by_video_id(v3.id)
        if len(v3_imgs) != 0: raise AssertionError("Atomicity failed: rows persisted")
        
        # Prove session usable
        img_repo.create({"video_id": v3.id, "sequence_index": 1, "prompt": "Recovered", "file_path": "/rec"})
        v3_imgs_after = img_repo.get_by_video_id(v3.id)
        if len(v3_imgs_after) != 1: raise AssertionError("Session unusable after rollback")
        
        # TEST 9 - DELETE SINGLE
        print("\n[Test 9] Delete Single")
        v3_img_id = v3_imgs_after[0].id
        res = img_repo.delete(v3_img_id)
        if res is not True: raise AssertionError("Delete returned False")
        if img_repo.get_by_id(v3_img_id) is not None: raise AssertionError("Record still exists")
        
        # TEST 10 - DELETE BY VIDEO ID
        print("\n[Test 10] Delete By Video ID")
        del_count = img_repo.delete_by_video_id(v2.id)
        if del_count != 2: raise AssertionError(f"Deleted {del_count} instead of 2")
        if len(img_repo.get_by_video_id(v2.id)) != 0: raise AssertionError("Records remain")
        if len(img_repo.get_by_video_id(v1.id)) != 4: raise AssertionError("V1 records affected")
        
        # TEST 11 - MISSING RECORD BEHAVIOR
        print("\n[Test 11] Missing Record Behavior")
        try:
            img_repo.delete(uuid.uuid4())
            raise AssertionError("Allowed delete missing record")
        except ValueError as e:
            if "not found" not in str(e).lower(): raise AssertionError("Wrong error msg")
            
    except Exception:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        print("\n[Cleanup] Removing temporary database records...")
        if v1: img_repo.delete_by_video_id(v1.id)
        if v2: img_repo.delete_by_video_id(v2.id)
        if v3: img_repo.delete_by_video_id(v3.id)
        
        if v1:
            try: video_repo.delete(v1.id)
            except Exception: pass
        if v2:
            try: video_repo.delete(v2.id)
            except Exception: pass
        if v3:
            try: video_repo.delete(v3.id)
            except Exception: pass
            
        if test_channel:
            try: channel_repo.delete(test_channel.id)
            except Exception: pass
            
        db.close()
        
    print("\n--- All GeneratedImageRepository Tests Passed ---")

if __name__ == "__main__":
    run_tests()
