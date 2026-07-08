import sys
import os
import uuid
import traceback

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient
from fastapi import Depends

# Import the actual application
from backend.main import app
from backend.config.session import SessionLocal
from backend.repositories.channel_repository import ChannelRepository
from backend.repositories.video_repository import VideoRepository

from backend.providers.text.dependency import get_text_provider
from backend.providers.text.fake import FakeTextGenerationProvider
from backend.providers.text.base import TextGenerationProvider
from backend.api.dependencies import get_video_service_dependency
from backend.services.video_service import VideoService

def run_tests():
    print("--- Starting Real API Routes Dependency Integration Tests ---")
    
    # 1. Override the provider dependency securely for the test
    def override_get_text_provider() -> TextGenerationProvider:
        return FakeTextGenerationProvider()
        
    app.dependency_overrides[get_text_provider] = override_get_text_provider
    
    # 2. Add temporary test-only endpoint directly to the imported app instance
    @app.get("/test/video-service-provider")
    def test_provider_endpoint(service: VideoService = Depends(get_video_service_dependency)):
        return {
            "provider_type": type(service.text_provider).__name__
        }

    # Initialize client after all overrides and test endpoints are registered
    client = TestClient(app)
    
    # Open setup/cleanup database session
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
        
        # Test 1: POST video creation
        print("\n[Test 1] POST /videos/ (creation via migrated route)")
        topic = "FastAPI Dependency Injection Integration Test"
        
        response = client.post(
            "/videos/",
            json={
                "channel_id": str(test_channel.id),
                "topic": topic
            }
        )
        
        if response.status_code != 201:
            raise AssertionError(f"Expected HTTP 201, got {response.status_code}. Response: {response.text}")
            
        data = response.json()
        if data.get("status") != "CREATED":
            raise AssertionError(f"Expected status CREATED, got {data.get('status')}")
            
        if data.get("channel_id") != str(test_channel.id):
            raise AssertionError(f"Expected channel_id {test_channel.id}, got {data.get('channel_id')}")
            
        if data.get("topic") != topic:
            raise AssertionError(f"Expected topic '{topic}', got '{data.get('topic')}'")
            
        test_video_id = data.get("id")
        print("  -> PASS: Video created through migrated real API route.")

        # Test 2: Valid status transition
        print("\n[Test 2] PATCH /videos/{video_id}/status (valid transition)")
        response = client.patch(
            f"/videos/{test_video_id}/status",
            json={
                "status": "PROCESSING"
            }
        )
        
        if response.status_code != 200:
            raise AssertionError(f"Expected HTTP 200, got {response.status_code}. Response: {response.text}")
            
        data = response.json()
        if data.get("status") != "PROCESSING":
            raise AssertionError(f"Expected status PROCESSING, got {data.get('status')}")
            
        print("  -> PASS: Valid status transition succeeded through migrated real API route.")

        # Test 3: Invalid status transition rejection
        print("\n[Test 3] PATCH /videos/{video_id}/status (invalid transition rejection)")
        # At this point the video is PROCESSING, so PROCESSING -> APPROVED must be rejected
        response = client.patch(
            f"/videos/{test_video_id}/status",
            json={
                "status": "APPROVED"
            }
        )
        
        if response.status_code != 400:
            raise AssertionError(f"Expected HTTP 400 for bad transition, got {response.status_code}. Response: {response.text}")
            
        data = response.json()
        if "Invalid status transition" not in data.get("detail", ""):
            raise AssertionError(f"Expected error detail to mention 'Invalid status transition', got '{data.get('detail')}'")
            
        print("  -> PASS: Invalid status transition appropriately rejected by business rules via migrated real API route.")

        # Test 4: Verify injected provider
        print("\n[Test 4] Verify configured provider is actually present in injected VideoService")
        response = client.get("/test/video-service-provider")
        
        if response.status_code != 200:
            raise AssertionError(f"Expected HTTP 200, got {response.status_code}. Response: {response.text}")
            
        data = response.json()
        if data.get("provider_type") != "FakeTextGenerationProvider":
            raise AssertionError(f"Expected provider_type FakeTextGenerationProvider, got {data.get('provider_type')}")
            
        print("  -> PASS: The injected VideoService definitively contains the configured FakeTextGenerationProvider.")

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
        
    print("--- All tests passed! Real API Routes successfully integrated with dependency injection. ---")

if __name__ == "__main__":
    run_tests()
