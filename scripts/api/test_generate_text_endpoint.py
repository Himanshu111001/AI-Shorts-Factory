import sys
import os
import uuid
import traceback

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient

from backend.main import app
from backend.config.session import SessionLocal
from backend.repositories.channel_repository import ChannelRepository
from backend.repositories.video_repository import VideoRepository
from backend.providers.text.dependency import get_text_provider
from backend.providers.text.fake import FakeTextGenerationProvider
from backend.providers.text.base import TextGenerationProvider

def run_tests():
    print("--- Starting Generate Text API Endpoint Integration Tests ---")
    
    # 1. Override the provider dependency for determinism
    def override_get_text_provider() -> TextGenerationProvider:
        return FakeTextGenerationProvider()
        
    app.dependency_overrides[get_text_provider] = override_get_text_provider

    client = TestClient(app)
    db = SessionLocal()
    
    test_channel = None
    test_video_id = None
    
    channel_repo = ChannelRepository(db)
    video_repo = VideoRepository(db)
    
    try:
        print("\n[Setup] Creating temporary test channel via repository...")
        channel_name = f"API Routes Test Channel {uuid.uuid4().hex[:8]}"
        test_channel = channel_repo.create({
            "name": channel_name,
            "niche": "Testing",
            "youtube_account": f"api_test_{uuid.uuid4().hex[:8]}",
            "is_active": True
        })
        
        # Setup: Create Video via API
        topic = "Integration Testing the Text Endpoint"
        response = client.post(
            "/videos/",
            json={
                "channel_id": str(test_channel.id),
                "topic": topic
            }
        )
        assert response.status_code == 201, f"Failed to create video: {response.text}"
        test_video_id = response.json()["id"]

        # Test 1 (Negative): generate-text while CREATED
        print("\n[Test 1] Negative Test: generate-text while CREATED")
        response = client.post(f"/videos/{test_video_id}/generate-text")
        
        if response.status_code != 400:
            raise AssertionError(f"Expected HTTP 400, got {response.status_code}. Response: {response.text}")
            
        data = response.json()
        if "Text generation requires PROCESSING status" not in data.get("detail", ""):
            raise AssertionError(f"Expected 'Text generation requires PROCESSING status', got {data.get('detail')}")
            
        print("  -> PASS: Correctly rejected generation for CREATED video.")

        # Transition Video to PROCESSING
        print("\n[Setup] Transitioning video to PROCESSING...")
        response = client.patch(
            f"/videos/{test_video_id}/status",
            json={"status": "PROCESSING"}
        )
        assert response.status_code == 200, f"Failed to update status: {response.text}"

        # Test 2: Happy Path Text Generation
        print("\n[Test 2] Happy Path: POST /videos/{video_id}/generate-text")
        response = client.post(f"/videos/{test_video_id}/generate-text")
        
        if response.status_code != 200:
            raise AssertionError(f"Expected HTTP 200, got {response.status_code}. Response: {response.text}")
            
        data = response.json()
        
        # Values from FakeTextGenerationProvider logic
        expected_title = "Integration Testing the Text Endpoint | Testing"
        expected_desc = "A short video about Integration Testing the Text Endpoint. Created for the Testing niche."
        expected_script = "Today we're talking about Integration Testing the Text Endpoint. This content is for viewers interested in Testing."
        expected_hashtags = ["#integration_testing_the_text_endpoint", "#testing", "#fake_generated"]
        
        if data.get("title") != expected_title:
            raise AssertionError(f"Title mismatch. Expected '{expected_title}', got '{data.get('title')}'")
        if data.get("description") != expected_desc:
            raise AssertionError(f"Description mismatch. Expected '{expected_desc}', got '{data.get('description')}'")
        if data.get("script") != expected_script:
            raise AssertionError(f"Script mismatch. Expected '{expected_script}', got '{data.get('script')}'")
        if data.get("hashtags") != expected_hashtags:
            raise AssertionError(f"Hashtags mismatch. Expected {expected_hashtags}, got {data.get('hashtags')}")
            
        print("  -> PASS: Text generation returned correctly formatted payload via API.")
        
        # Test 3: DB Persistence Verification
        print("\n[Test 3] Verifying database persistence via Repository...")
        # Clear identity map cache by opening a fresh query
        db.expire_all() 
        db_video = video_repo.get_by_id(uuid.UUID(test_video_id))
        
        if db_video.title != expected_title or db_video.description != expected_desc:
            raise AssertionError("Database did not correctly persist generated fields.")
            
        print("  -> PASS: Text content was properly persisted to the database.")

        # Test 4 (Negative): Random UUID
        print("\n[Test 4] Negative Test: generate-text for random UUID")
        random_uuid = uuid.uuid4()
        response = client.post(f"/videos/{random_uuid}/generate-text")
        
        if response.status_code != 404:
            raise AssertionError(f"Expected HTTP 404, got {response.status_code}. Response: {response.text}")
            
        if "Video not found" not in response.json().get("detail", ""):
             raise AssertionError(f"Expected 'Video not found' error, got {response.text}")
             
        print("  -> PASS: Correctly returned 404 for non-existent video.")

    except Exception:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        raise
        
    finally:
        print("\n[Cleanup] Removing temporary database records and clearing overrides...")
        if test_video_id:
            try:
                video_repo.delete(uuid.UUID(test_video_id))
                print(f"  -> Deleted temporary video: {test_video_id}")
            except Exception as e:
                print(f"  -> Failed to delete temporary video: {e}")
                
        if test_channel:
            try:
                channel_repo.delete(test_channel.id)
                print(f"  -> Deleted temporary channel: {test_channel.id}")
            except Exception as e:
                print(f"  -> Failed to delete temporary channel: {e}")
                
        db.close()
        app.dependency_overrides.clear()
        
    print("--- All tests passed! generate-text API endpoint works as expected. ---")

if __name__ == "__main__":
    run_tests()
