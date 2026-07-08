import sys
import os
import uuid
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient

from backend.main import app
from backend.config.database import engine
from backend.models.base import Base
from backend.config.session import SessionLocal
from backend.repositories.channel_repository import ChannelRepository
from backend.repositories.video_repository import VideoRepository
from backend.repositories.job_repository import JobRepository
from backend.services.job_service import JobService
from backend.models.enums.job_status import JobStatus

def run_tests():
    print("--- Starting Job Progress Observability Test ---")
    
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    db = SessionLocal()
    
    channel_repo = ChannelRepository(db)
    video_repo = VideoRepository(db)
    job_service = JobService(db)
    job_repo = JobRepository(db)
    
    test_channel = None
    test_video = None
    job_id = None
    
    try:
        print("\n[Setup] Creating temporary test channel, video...")
        test_channel = channel_repo.create({
            "name": "Progress Obs Test Channel",
            "niche": "Testing",
            "youtube_account": f"prog_obs_{uuid.uuid4().hex[:8]}",
            "is_active": True
        })
        test_video = video_repo.create({
            "channel_id": test_channel.id,
            "topic": "Progress Observability Topic"
        })
        
        response = client.post(f"/jobs/video/{test_video.id}")
        job_id = response.json()["id"]
        job_uuid = uuid.UUID(job_id)
        
        print("\n[Test 1] Verify initial QUEUED state")
        res = client.get(f"/jobs/{job_id}")
        if res.status_code != 200: raise AssertionError(f"Expected 200, got {res.status_code}")
        data = res.json()
        if data["status"] != "QUEUED": raise AssertionError("Not QUEUED")
        if data["progress"] != 0: raise AssertionError("Progress not 0")
        if data["current_step"] is not None: raise AssertionError("current_step not null")
        
        print("\n[Test 2] Verify state after start_job")
        job_service.start_job(job_uuid)
        res = client.get(f"/jobs/{job_id}")
        data = res.json()
        if data["status"] != "RUNNING": raise AssertionError("Not RUNNING")
        
        print("\n[Test 3] Verify update 10, 'Generating Text'")
        job_service.update_progress(job_uuid, 10, "Generating Text")
        res = client.get(f"/jobs/{job_id}")
        data = res.json()
        if data["progress"] != 10: raise AssertionError("Progress not 10")
        if data["current_step"] != "Generating Text": raise AssertionError("Wrong step")
        
        print("\n[Test 4] Verify update 35, 'Text Generated'")
        job_service.update_progress(job_uuid, 35, "Text Generated")
        res = client.get(f"/jobs/{job_id}")
        data = res.json()
        if data["progress"] != 35: raise AssertionError("Progress not 35")
        if data["current_step"] != "Text Generated": raise AssertionError("Wrong step")
        
        print("\n[Test 5] Verify update 40, 'Generating Audio'")
        job_service.update_progress(job_uuid, 40, "Generating Audio")
        res = client.get(f"/jobs/{job_id}")
        data = res.json()
        if data["progress"] != 40: raise AssertionError("Progress not 40")
        if data["current_step"] != "Generating Audio": raise AssertionError("Wrong step")
        
        print("\n[Test 6] Verify update 60, 'Audio Generated'")
        job_service.update_progress(job_uuid, 60, "Audio Generated")
        res = client.get(f"/jobs/{job_id}")
        data = res.json()
        if data["progress"] != 60: raise AssertionError("Progress not 60")
        if data["current_step"] != "Audio Generated": raise AssertionError("Wrong step")
        
        print("\n[Test 7] Verify update 65, 'Generating Images'")
        job_service.update_progress(job_uuid, 65, "Generating Images")
        res = client.get(f"/jobs/{job_id}")
        data = res.json()
        if data["progress"] != 65: raise AssertionError("Progress not 65")
        if data["current_step"] != "Generating Images": raise AssertionError("Wrong step")
        
        print("\n[Test 8] Verify update 90, 'Images Generated'")
        job_service.update_progress(job_uuid, 90, "Images Generated")
        res = client.get(f"/jobs/{job_id}")
        data = res.json()
        if data["progress"] != 90: raise AssertionError("Progress not 90")
        if data["current_step"] != "Images Generated": raise AssertionError("Wrong step")
        
        print("\n[Test 9] Verify state after complete_job")
        job_service.complete_job(job_uuid)
        res = client.get(f"/jobs/{job_id}")
        data = res.json()
        if data["status"] != "COMPLETED": raise AssertionError("Not COMPLETED")
        if data["progress"] != 100: raise AssertionError("Progress not 100")
        if data["current_step"] != "Completed": raise AssertionError("Wrong step")
        if data["finished_at"] is None: raise AssertionError("finished_at is null")
        
    except Exception:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        print("\n[Cleanup] Removing temporary database records...")
        if job_id:
            try:
                job_repo.delete(job_uuid)
            except Exception:
                pass
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
        
    print("\n--- All tests passed! Job Progress Observability works as expected. ---")

if __name__ == "__main__":
    run_tests()
