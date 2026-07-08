import sys
import os
import traceback
from fastapi import FastAPI, Depends
from fastapi.testclient import TestClient

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.api.dependencies import get_video_service_dependency
from backend.services.video_service import VideoService
from backend.providers.text.dependency import get_text_provider
from backend.providers.text.fake import FakeTextGenerationProvider
from backend.providers.text.base import TextGenerationProvider

def run_tests():
    print("--- Starting FastAPI Dependency Integration Tests ---")
    
    # 1. Stand up a temporary minimal app exclusively for this test
    app = FastAPI()

    # 2. Add an anonymous test endpoint that demands VideoService via the new Depends wrapper
    @app.get("/test-video-service-dependency")
    def test_dependency_endpoint(service: VideoService = Depends(get_video_service_dependency)):
        return {
            "service_type": type(service).__name__,
            "provider_type": type(service.text_provider).__name__,
            "has_video_repo": getattr(service, "video_repo", None) is not None,
            "has_channel_repo": getattr(service, "channel_repo", None) is not None,
            "shared_db_session": (
                service.video_repo.db is service.db
                and service.channel_repo.db is service.db
            ),
        }

    # 3. Create a deterministic provider dependency for the test
    def override_get_text_provider() -> TextGenerationProvider:
        return FakeTextGenerationProvider()
        
    # Wire the override securely into FastAPI.
    # This prevents the test from altering OS environment variables or app-wide Settings state.
    app.dependency_overrides[get_text_provider] = override_get_text_provider
    
    # Initialize the client AFTER overrides are set
    client = TestClient(app)

    try:
        print("\n[Test 1] Dispatching TestClient request to resolve FastAPI Depends graph...")
        
        # Fire request - this asks FastAPI to unpack the Depends DAG under the hood
        response = client.get("/test-video-service-dependency")
        
        if response.status_code != 200:
            raise AssertionError(f"Expected HTTP 200 OK, got {response.status_code}. Response: {response.text}")
        print("  -> PASS: Endpoint resolved without server errors.")
        
        data = response.json()
        
        if data.get("service_type") != "VideoService":
            raise AssertionError(f"Expected service_type 'VideoService', got '{data.get('service_type')}'")
        print("  -> PASS: Resolved object is VideoService.")
        
        if data.get("provider_type") != "FakeTextGenerationProvider":
            raise AssertionError(f"Expected provider_type 'FakeTextGenerationProvider', got '{data.get('provider_type')}'")
        print("  -> PASS: FastAPI successfully honored the text provider dependency override.")
        
        if not data.get("has_video_repo"):
            raise AssertionError("VideoRepository was not correctly constructed.")
        print("  -> PASS: VideoRepository correctly initialized.")
        
        if not data.get("has_channel_repo"):
            raise AssertionError("ChannelRepository was not correctly constructed.")
        print("  -> PASS: ChannelRepository correctly initialized.")
        
        if not data.get("shared_db_session"):
            raise AssertionError("Repository db sessions do not match the injected parent session.")
        print("  -> PASS: Repositories cleanly share the FastAPI request-scoped DB session.")

    except Exception:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        raise
        
    finally:
        print("\n[Cleanup] Clearing FastAPI dependency overrides...")
        app.dependency_overrides.clear()
        
    print("--- All tests passed! FastAPI successfully resolves the full dependency chain. ---")

if __name__ == "__main__":
    run_tests()
