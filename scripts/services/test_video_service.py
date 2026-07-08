import sys
import os
import uuid
import traceback

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# 1. Imports to ensure SQLAlchemy metadata is populated
from backend.models.base import Base
from backend.models.channel import Channel
from backend.models.video import Video
from backend.models.enums.video_status import VideoStatus

from backend.config.database import engine
from backend.config.session import SessionLocal
from backend.repositories.channel_repository import ChannelRepository
from backend.services.video_service import VideoService

def run_video_service_tests():
    print("--- Starting VideoService Business Rules Verification ---")
    
    # 2. Ensure required tables exist
    Base.metadata.create_all(bind=engine)
    
    # 3. Open a database session
    db = SessionLocal()
    
    # 4. Initialize dependencies
    channel_repo = ChannelRepository(db)
    video_service = VideoService(db)
    
    test_channel = None
    test_video = None
    
    try:
        # 5. Create a temporary active test channel
        print("\n[Setup] Creating temporary test channel...")
        test_channel = channel_repo.create({
            "name": "Test VideoService Channel",
            "niche": "Testing & QA",
            "youtube_account": "test_vservice_123",
            "is_active": True
        })
        print(f"  -> Created channel ID: {test_channel.id}")

        # 6. Test successful video creation
        print("\n[Test 1] Video creation for active channel")
        test_video = video_service.create_video({
            "channel_id": test_channel.id,
            "topic": "How to write standalone integration tests"
        })
        
        if test_video.status == VideoStatus.CREATED:
            print("  -> PASS: Video created successfully and initial status is CREATED.")
        else:
            raise AssertionError(f"Expected CREATED but got {test_video.status}")

        # 7. Test valid transition: CREATED -> PROCESSING
        print("\n[Test 2] Valid state transition: CREATED -> PROCESSING")
        test_video = video_service.transition_status(test_video.id, VideoStatus.PROCESSING)
        if test_video.status == VideoStatus.PROCESSING:
            print("  -> PASS: Transitioned successfully.")
        else:
            raise AssertionError("Transition to PROCESSING failed.")

        # 8. Test valid transition: PROCESSING -> REVIEW
        print("\n[Test 3] Valid state transition: PROCESSING -> REVIEW")
        test_video = video_service.transition_status(test_video.id, VideoStatus.REVIEW)
        if test_video.status == VideoStatus.REVIEW:
            print("  -> PASS: Transitioned successfully.")
        else:
            raise AssertionError("Transition to REVIEW failed.")

        # 9. Test invalid transition: REVIEW -> UPLOADED
        print("\n[Test 4] Invalid state transition: REVIEW -> UPLOADED")
        try:
            video_service.transition_status(test_video.id, VideoStatus.UPLOADED)
            raise AssertionError("Allowed an invalid transition (REVIEW -> UPLOADED)!")
        except ValueError as e:
            print(f"  -> PASS: Caught expected ValueError: '{e}'")

        # 10. Test video creation with nonexistent channel
        print("\n[Test 5] Video creation with non-existent channel UUID")
        fake_uuid = uuid.uuid4()
        try:
            video_service.create_video({
                "channel_id": fake_uuid,
                "topic": "Should fail because channel doesn't exist"
            })
            raise AssertionError("Allowed creation for non-existent channel!")
        except ValueError as e:
            if "Channel not found" in str(e):
                print(f"  -> PASS: Caught expected ValueError: '{e}'")
            else:
                raise AssertionError(f"Wrong ValueError raised: '{e}'")

        # 11. Test video creation with inactive channel
        print("\n[Test 6] Video creation with inactive channel")
        channel_repo.update(test_channel.id, {"is_active": False})
        try:
            video_service.create_video({
                "channel_id": test_channel.id,
                "topic": "Should fail because channel is inactive"
            })
            raise AssertionError("Allowed creation for inactive channel!")
        except ValueError as e:
            if "Channel is inactive" in str(e):
                print(f"  -> PASS: Caught expected ValueError: '{e}'")
            else:
                raise AssertionError(f"Wrong ValueError raised: '{e}'")

    except Exception as e:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        raise
        
    finally:
        # 12. Clean up all temporary test data
        print("\n[Cleanup] Cleaning up database state...")
        
        if test_video:
            try:
                # Video depends on Channel, so delete Video first
                video_service.video_repo.delete(test_video.id)
                print(f"  -> Deleted test video: {test_video.id}")
            except Exception as e:
                print(f"  -> Error deleting test video: {e}")
                
        if test_channel:
            try:
                channel_repo.delete(test_channel.id)
                print(f"  -> Deleted test channel: {test_channel.id}")
            except Exception as e:
                print(f"  -> Error deleting test channel: {e}")
                
        db.close()
        print("--- VideoService Tests Complete ---")

if __name__ == "__main__":
    run_video_service_tests()
