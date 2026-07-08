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
    print("--- Starting Job API Endpoint Integration Tests ---")
    
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    client = TestClient(app)
    db = SessionLocal()
    
    channel_repo = ChannelRepository(db)
    video_repo = VideoRepository(db)
    job_repo = JobRepository(db)
    job_service = JobService(db)
    
    test_channel = None
    test_video_id = None
    created_job_ids = []
    
    try:
        # Setup
        print("\n[Setup] Creating temporary test channel via repository...")
        channel_name = f"API Routes Test Channel {uuid.uuid4().hex[:8]}"
        test_channel = channel_repo.create({
            "name": channel_name,
            "niche": "Testing",
            "youtube_account": f"api_test_{uuid.uuid4().hex[:8]}",
            "is_active": True
        })
        
        # Setup: Create Video via API (as requested)
        topic = "Integration Testing the Job API"
        response = client.post(
            "/videos/",
            json={
                "channel_id": str(test_channel.id),
                "topic": topic
            }
        )
        assert response.status_code == 201, f"Failed to create video: {response.text}"
        test_video_id = response.json()["id"]

        # TEST 1
        print("\n[Test 1] Create Job (POST /jobs/video/{video_id})")
        response = client.post(f"/jobs/video/{test_video_id}")
        if response.status_code != 201:
            raise AssertionError(f"Expected HTTP 201, got {response.status_code}. Response: {response.text}")
            
        data = response.json()
        job1_id = data["id"]
        created_job_ids.append(job1_id)
        
        if data["video_id"] != test_video_id: raise AssertionError("video_id mismatch")
        if data["status"] != "QUEUED": raise AssertionError("status not QUEUED")
        if data["progress"] != 0: raise AssertionError("progress not 0")
        if data["current_step"] is not None: raise AssertionError("current_step not null")
        if data["error"] is not None: raise AssertionError("error not null")
        if "created_at" not in data: raise AssertionError("created_at missing")
        if data["started_at"] is not None: raise AssertionError("started_at not null")
        if data["finished_at"] is not None: raise AssertionError("finished_at not null")

        # TEST 2
        print("\n[Test 2] Verify database persistence")
        db_job1 = job_repo.get_by_id(uuid.UUID(job1_id))
        if not db_job1: raise AssertionError("Job not found in DB")
        if db_job1.status != JobStatus.QUEUED: raise AssertionError("DB status not QUEUED")
        if db_job1.progress != 0: raise AssertionError("DB progress not 0")
        if str(db_job1.video_id) != test_video_id: raise AssertionError("DB video_id mismatch")

        # TEST 3
        print("\n[Test 3] Duplicate active Job conflict")
        response = client.post(f"/jobs/video/{test_video_id}")
        if response.status_code != 409:
            raise AssertionError(f"Expected HTTP 409, got {response.status_code}. Response: {response.text}")
        if response.json()["detail"] != "Video already has an active job":
            raise AssertionError(f"Wrong error message: {response.json()}")

        # TEST 4
        print("\n[Test 4] Get Job by ID (GET /jobs/{job_id})")
        response = client.get(f"/jobs/{job1_id}")
        if response.status_code != 200:
            raise AssertionError(f"Expected HTTP 200, got {response.status_code}. Response: {response.text}")
        data = response.json()
        if data["id"] != job1_id: raise AssertionError("ID mismatch")
        if data["video_id"] != test_video_id: raise AssertionError("video_id mismatch")
        if data["status"] != "QUEUED": raise AssertionError("status not QUEUED")
        if data["progress"] != 0: raise AssertionError("progress not 0")

        # TEST 5
        print("\n[Test 5] List Jobs for Video (GET /jobs/video/{video_id})")
        response = client.get(f"/jobs/video/{test_video_id}")
        if response.status_code != 200:
            if response.status_code == 422:
                print(f"\n[ROUTE ORDERING BUG] Request to /jobs/video/UUID failed with 422: {response.text}")
            raise AssertionError(f"Expected HTTP 200, got {response.status_code}. Response: {response.text}")
            
        data = response.json()
        if not isinstance(data, list): raise AssertionError("Response is not a list")
        if len(data) != 1: raise AssertionError(f"Expected 1 job, got {len(data)}")
        if data[0]["id"] != job1_id: raise AssertionError("Returned Job ID mismatch")

        # TEST 6
        print("\n[Test 6] Prepare historical Job attempt")
        # Start and fail job1 using service
        job_service.start_job(uuid.UUID(job1_id))
        job_service.fail_job(uuid.UUID(job1_id), "Simulated historical failure")
        
        # Create second job
        response = client.post(f"/jobs/video/{test_video_id}")
        if response.status_code != 201:
            raise AssertionError(f"Expected HTTP 201, got {response.status_code}. Response: {response.text}")
        data = response.json()
        job2_id = data["id"]
        created_job_ids.append(job2_id)
        if data["status"] != "QUEUED": raise AssertionError("Second job not QUEUED")
        if job2_id == job1_id: raise AssertionError("Second job has same ID as first")

        # TEST 7
        print("\n[Test 7] Verify newest-first history ordering")
        response = client.get(f"/jobs/video/{test_video_id}")
        if response.status_code != 200:
            raise AssertionError(f"Expected HTTP 200, got {response.status_code}. Response: {response.text}")
        data = response.json()
        if len(data) != 2: raise AssertionError(f"Expected 2 jobs, got {len(data)}")
        
        if data[0]["id"] != job2_id: raise AssertionError("Second job not first in list")
        if data[1]["id"] != job1_id: raise AssertionError("First job not second in list")
        
        if data[1]["status"] != "FAILED": raise AssertionError("First job status not FAILED")
        if data[1]["error"] != "Simulated historical failure": raise AssertionError("First job error mismatch")
        if data[0]["status"] != "QUEUED": raise AssertionError("Second job status not QUEUED")

        # TEST 8
        print("\n[Test 8] Missing Job")
        response = client.get(f"/jobs/{uuid.uuid4()}")
        if response.status_code != 404: raise AssertionError(f"Expected 404, got {response.status_code}")
        if response.json()["detail"] != "Job not found": raise AssertionError("Wrong detail message")

        # TEST 9
        print("\n[Test 9] Missing Video when creating Job")
        response = client.post(f"/jobs/video/{uuid.uuid4()}")
        if response.status_code != 404: raise AssertionError(f"Expected 404, got {response.status_code}")
        if response.json()["detail"] != "Video not found": raise AssertionError("Wrong detail message")

        # TEST 10
        print("\n[Test 10] Missing Video when listing Jobs")
        response = client.get(f"/jobs/video/{uuid.uuid4()}")
        if response.status_code != 404: raise AssertionError(f"Expected 404, got {response.status_code}")
        if response.json()["detail"] != "Video not found": raise AssertionError("Wrong detail message")

    except Exception:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        print("\n[Cleanup] Removing temporary database records...")
        for j_id in created_job_ids:
            try:
                job_repo.delete(uuid.UUID(j_id))
                print(f"  -> Deleted test job: {j_id}")
            except Exception as e:
                print(f"  -> Failed to delete test job {j_id}: {e}")
                
        if test_video_id:
            try:
                video_repo.delete(uuid.UUID(test_video_id))
                print(f"  -> Deleted test video: {test_video_id}")
            except Exception as e:
                print(f"  -> Failed to delete test video: {e}")
                
        if test_channel:
            try:
                channel_repo.delete(test_channel.id)
                print(f"  -> Deleted test channel: {test_channel.id}")
            except Exception as e:
                print(f"  -> Failed to delete test channel: {e}")
                
        db.close()
        
    print("--- All tests passed! Job API endpoints work as expected. ---")

if __name__ == "__main__":
    run_tests()
