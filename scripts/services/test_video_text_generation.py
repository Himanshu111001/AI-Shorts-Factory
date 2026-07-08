import sys
import os
import uuid
import traceback

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.models.base import Base
from backend.models.enums.video_status import VideoStatus
from backend.config.database import engine
from backend.config.session import SessionLocal
from backend.repositories.channel_repository import ChannelRepository
from backend.services.video_service import VideoService
from backend.providers.text.fake import FakeTextGenerationProvider

def run_integration_tests():
    print("--- Starting Video Text Generation Integration Tests ---")
    
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    channel_repo = ChannelRepository(db)
    
    provider = FakeTextGenerationProvider()
    video_service = VideoService(db, text_provider=provider)
    
    test_channel = None
    test_video = None
    
    try:
        print("\n[Setup] Creating temporary active test channel...")
        test_channel = channel_repo.create({
            "name": f"Integration Test Channel {uuid.uuid4().hex[:8]}",
            "niche": "AI Tech",
            "youtube_account": "integration_test_ai",
            "is_active": True
        })
        
        topic = "Integration Testing Basics"
        niche = test_channel.niche

        print("\n[Test 1] Video creation...")
        test_video = video_service.create_video({
            "channel_id": test_channel.id,
            "topic": topic
        })
        
        if test_video.status != VideoStatus.CREATED:
            raise AssertionError(f"Expected status CREATED, got {test_video.status}")
        print("  -> PASS: Video created with status CREATED.")

        print("\n[Test 2] Text generation rejected when status is CREATED...")
        try:
            video_service.generate_text_content(test_video.id)
            raise AssertionError("Text generation should have failed when status is CREATED.")
        except ValueError as e:
            if "requires PROCESSING status" in str(e):
                print(f"  -> PASS: Caught expected ValueError: '{e}'")
            else:
                raise AssertionError(f"Wrong ValueError raised: '{e}'")

        print("\n[Test 3] Valid transition to PROCESSING...")
        test_video = video_service.transition_status(test_video.id, VideoStatus.PROCESSING)
        if test_video.status != VideoStatus.PROCESSING:
            raise AssertionError("Failed to transition video to PROCESSING.")
        print("  -> PASS: Video is now PROCESSING.")

        print("\n[Test 4] Successful text generation orchestration...")
        updated_video = video_service.generate_text_content(test_video.id)
        
        expected_title = "Integration Testing Basics | AI Tech"
        expected_desc = "A short video about Integration Testing Basics. Created for the AI Tech niche."
        expected_script = "Today we're talking about Integration Testing Basics. This content is for viewers interested in AI Tech."
        expected_hashtags = ["#integration_testing_basics", "#ai_tech", "#fake_generated"]
        
        if updated_video.title != expected_title:
            raise AssertionError(f"Unexpected title: {updated_video.title}")
        if updated_video.description != expected_desc:
            raise AssertionError(f"Unexpected description: {updated_video.description}")
        if updated_video.script != expected_script:
            raise AssertionError(f"Unexpected script: {updated_video.script}")
        if updated_video.hashtags != expected_hashtags:
            raise AssertionError(f"Unexpected hashtags: {updated_video.hashtags}")
            
        print("  -> PASS: Returned video object contains exact expected generated values.")

        print("\n[Test 5] Status must remain PROCESSING...")
        if updated_video.status != VideoStatus.PROCESSING:
            raise AssertionError(f"Status unexpectedly changed from PROCESSING to {updated_video.status}")
        print("  -> PASS: Status remains PROCESSING.")

        print("\n[Test 6] Database persistence verification...")
        # Refetch directly from DB to verify it's not just a memory update
        refetched_video = video_service.video_repo.get_by_id(test_video.id)
        
        if refetched_video.title != expected_title or \
           refetched_video.description != expected_desc or \
           refetched_video.script != expected_script or \
           refetched_video.hashtags != expected_hashtags:
            raise AssertionError("Generated content was not properly persisted to the database.")
        print("  -> PASS: Refetched video has all generated content perfectly persisted.")

        print("\n[Test 7] Missing provider behavior...")
        service_without_provider = VideoService(db)
        try:
            service_without_provider.generate_text_content(test_video.id)
            raise AssertionError("Should fail without a configured text provider.")
        except ValueError as e:
            if "provider is not configured" in str(e):
                print(f"  -> PASS: Caught expected ValueError: '{e}'")
            else:
                raise AssertionError(f"Wrong ValueError raised: '{e}'")
                
    except Exception as e:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        raise
        
    finally:
        print("\n[Cleanup] Cleaning up database state...")
        if test_video:
            try:
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
        print("--- Integration Tests Complete ---")

if __name__ == "__main__":
    run_integration_tests()
