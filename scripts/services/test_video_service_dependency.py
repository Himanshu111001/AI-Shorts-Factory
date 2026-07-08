import sys
import os
import traceback

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.session import SessionLocal
from backend.providers.text.fake import FakeTextGenerationProvider
from backend.services.video_service import VideoService
from backend.services.dependency import get_video_service

def run_tests():
    print("--- Starting Video Service Dependency Assembly Verification ---")
    
    db = SessionLocal()
    
    try:
        print("\n[Test 1] Object Assembly & Identity Verification")
        
        provider = FakeTextGenerationProvider()
        
        service = get_video_service(
            db=db,
            text_provider=provider,
        )
        
        if not isinstance(service, VideoService):
            raise AssertionError("service is not an instance of VideoService")
        print("  -> PASS: service is an instance of VideoService")
            
        if service.db is not db:
            raise AssertionError("Injected db identity mismatch")
        print("  -> PASS: service.db is the exact same database session object")
            
        if service.text_provider is not provider:
            raise AssertionError("Injected provider identity mismatch")
        print("  -> PASS: service.text_provider is the exact same provider object")
            
        if service.video_repo.db is not db:
            raise AssertionError("video_repo.db identity mismatch")
        print("  -> PASS: service.video_repo uses the exact same database session")
            
        if service.channel_repo.db is not db:
            raise AssertionError("channel_repo.db identity mismatch")
        print("  -> PASS: service.channel_repo uses the exact same database session")

    except Exception:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        raise
        
    finally:
        db.close()
        print("\n[Cleanup] Database session closed.")
        
    print("--- All tests passed! Video Service Dependency assembly works as expected. ---")

if __name__ == "__main__":
    run_tests()
