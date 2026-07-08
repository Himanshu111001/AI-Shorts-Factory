import sys
import os
import uuid
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.models.base import Base
from backend.models.enums.job_status import JobStatus
from backend.config.database import engine
from backend.config.session import SessionLocal
from backend.repositories.channel_repository import ChannelRepository
from backend.repositories.video_repository import VideoRepository
from backend.services.job_service import JobService

def run_job_service_tests():
    print("--- Starting JobService Integration Tests ---")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    channel_repo = ChannelRepository(db)
    video_repo = VideoRepository(db)
    job_service = JobService(db)
    
    test_channel = None
    test_video = None
    created_jobs = []
    
    try:
        # 1. Setup
        print("\n[Setup] Creating temporary test channel and video...")
        test_channel = channel_repo.create({
            "name": "Test JobService Channel",
            "niche": "Testing",
            "youtube_account": "job_service_test_123",
            "is_active": True
        })
        test_video = video_repo.create({
            "channel_id": test_channel.id,
            "topic": "Job Service Test Topic"
        })
        
        # 2. Test create_job()
        print("\n[Test 2] Test create_job()")
        job1 = job_service.create_job(test_video.id)
        created_jobs.append(job1)
        if not job1: raise AssertionError("returned object does not exist")
        if job1.video_id != test_video.id: raise AssertionError("job.video_id mismatch")
        if job1.status != JobStatus.QUEUED: raise AssertionError("status not QUEUED")
        if job1.progress != 0: raise AssertionError("progress != 0")
        if job1.current_step is not None: raise AssertionError("current_step not None")
        if job1.error is not None: raise AssertionError("error not None")
        if job1.started_at is not None: raise AssertionError("started_at not None")
        if job1.finished_at is not None: raise AssertionError("finished_at not None")
        
        # 3. Test duplicate active-job prevention while QUEUED
        print("\n[Test 3] duplicate active-job prevention while QUEUED")
        try:
            job_service.create_job(test_video.id)
            raise AssertionError("Allowed duplicate job while QUEUED")
        except ValueError as e:
            if str(e) != "Video already has an active job":
                raise AssertionError(f"Expected ValueError('Video already has an active job'), got: {e}")
                
        # 4. Test create_job() for nonexistent Video
        print("\n[Test 4] create_job() for nonexistent Video")
        try:
            job_service.create_job(uuid.uuid4())
            raise AssertionError("Allowed job creation for nonexistent video")
        except ValueError as e:
            if str(e) != "Video not found":
                raise AssertionError(f"Expected 'Video not found', got: {e}")
                
        # 5. Test start_job()
        print("\n[Test 5] start_job()")
        job1 = job_service.start_job(job1.id)
        if job1.status != JobStatus.RUNNING: raise AssertionError("status not RUNNING")
        if job1.started_at is None: raise AssertionError("started_at is None")
        if job1.progress != 0: raise AssertionError("progress not 0")
        if job1.error is not None: raise AssertionError("error not None")
        
        # 6. Test invalid start transition
        print("\n[Test 6] invalid start transition")
        try:
            job_service.start_job(job1.id)
            raise AssertionError("Allowed starting a RUNNING job")
        except ValueError as e:
            if str(e) != "Invalid job status transition: RUNNING -> RUNNING":
                raise AssertionError(f"Wrong error message: {e}")
                
        # 7. Test duplicate active-job prevention while RUNNING
        print("\n[Test 7] duplicate active-job prevention while RUNNING")
        try:
            job_service.create_job(test_video.id)
            raise AssertionError("Allowed duplicate active job while RUNNING")
        except ValueError as e:
            if str(e) != "Video already has an active job":
                raise AssertionError(f"Wrong error message: {e}")
                
        # 8. Test valid progress update
        print("\n[Test 8] valid progress update")
        job1 = job_service.update_progress(job1.id, 40, "Generating Text")
        if job1.progress != 40: raise AssertionError("progress not 40")
        if job1.current_step != "Generating Text": raise AssertionError("current_step mismatch")
        if job1.status != JobStatus.RUNNING: raise AssertionError("status not RUNNING")
        
        # 9. Test invalid progress ranges
        print("\n[Test 9] invalid progress ranges")
        for bad_prog in [-1, 101]:
            try:
                job_service.update_progress(job1.id, bad_prog, "Failed step")
                raise AssertionError(f"Allowed invalid progress {bad_prog}")
            except ValueError as e:
                if str(e) != "Job progress must be between 0 and 100":
                    raise AssertionError(f"Wrong error msg: {e}")
            job1 = job_service.get_job(job1.id)
            if job1.progress != 40:
                raise AssertionError("Progress was modified after failure")
                
        # 10. Test complete_job()
        print("\n[Test 10] complete_job()")
        job1 = job_service.complete_job(job1.id)
        if job1.status != JobStatus.COMPLETED: raise AssertionError("status not COMPLETED")
        if job1.progress != 100: raise AssertionError("progress not 100")
        if job1.current_step != "Completed": raise AssertionError("current_step not Completed")
        if job1.finished_at is None: raise AssertionError("finished_at is None")
        if job1.error is not None: raise AssertionError("error not None")
        
        # 11. Test progress update rejected after completion
        print("\n[Test 11] progress update rejected after completion")
        try:
            job_service.update_progress(job1.id, 99, "Testing")
            raise AssertionError("Allowed progress update on COMPLETED job")
        except ValueError as e:
            if str(e) != "Job progress can only be updated while RUNNING":
                raise AssertionError(f"Wrong error msg: {e}")
                
        # 12. Test invalid completion transition
        print("\n[Test 12] invalid completion transition")
        try:
            job_service.complete_job(job1.id)
            raise AssertionError("Allowed complete on COMPLETED job")
        except ValueError as e:
            if str(e) != "Invalid job status transition: COMPLETED -> COMPLETED":
                raise AssertionError(f"Wrong error msg: {e}")
                
        # 13. Test new attempt after completed job
        print("\n[Test 13] new attempt after completed job")
        job2 = job_service.create_job(test_video.id)
        created_jobs.append(job2)
        if job2.id == job1.id: raise AssertionError("new job has same ID as old job")
        if job2.status != JobStatus.QUEUED: raise AssertionError("new job not QUEUED")
        all_jobs = job_service.get_jobs_for_video(test_video.id)
        if len(all_jobs) != 2: raise AssertionError("Not all jobs retained in history")
        
        # 14. Test failure path
        print("\n[Test 14] failure path")
        job2 = job_service.start_job(job2.id)
        job2 = job_service.update_progress(job2.id, 55, "Generating Audio")
        job2 = job_service.fail_job(job2.id, "Audio provider unavailable")
        
        if job2.status != JobStatus.FAILED: raise AssertionError("status not FAILED")
        if job2.progress != 55: raise AssertionError("progress not 55")
        if job2.current_step != "Generating Audio": raise AssertionError("current_step mismatch")
        if job2.error != "Audio provider unavailable": raise AssertionError("error mismatch")
        if job2.finished_at is None: raise AssertionError("finished_at is None")
        
        # 15. Test invalid fail transition
        print("\n[Test 15] invalid fail transition")
        try:
            job_service.fail_job(job2.id, "Another error")
            raise AssertionError("Allowed fail on FAILED job")
        except ValueError as e:
            if str(e) != "Invalid job status transition: FAILED -> FAILED":
                raise AssertionError(f"Wrong error msg: {e}")
                
        # 16. Test retry after failed job
        print("\n[Test 16] retry after failed job")
        job3 = job_service.create_job(test_video.id)
        created_jobs.append(job3)
        
        # 17. Test get_job()
        print("\n[Test 17] get_job()")
        fetched_job = job_service.get_job(job2.id)
        if fetched_job.id != job2.id: raise AssertionError("Fetched wrong job ID")
        
        # 18. Test get_job() missing ID
        print("\n[Test 18] get_job() missing ID")
        try:
            job_service.get_job(uuid.uuid4())
            raise AssertionError("Fetched non-existent job")
        except ValueError as e:
            if str(e) != "Job not found": raise AssertionError(f"Wrong error msg: {e}")
            
        # 19. Test get_jobs_for_video()
        print("\n[Test 19] get_jobs_for_video()")
        jobs_history = job_service.get_jobs_for_video(test_video.id)
        if len(jobs_history) != 3: raise AssertionError("Expected 3 jobs in history")
        if jobs_history[0].id != job3.id: raise AssertionError("Newest job not first")
        if jobs_history[-1].id != job1.id: raise AssertionError("Oldest job not last")
        
        # 20. Test get_jobs_for_video() missing Video
        print("\n[Test 20] get_jobs_for_video() missing Video")
        try:
            job_service.get_jobs_for_video(uuid.uuid4())
            raise AssertionError("Allowed fetching jobs for missing video")
        except ValueError as e:
            if str(e) != "Video not found": raise AssertionError(f"Wrong error msg: {e}")
            
    except Exception:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        # 21. Cleanup
        print("\n[Cleanup] Cleaning up database state...")
        for j in created_jobs:
            try:
                job_service.job_repo.delete(j.id)
                print(f"  -> Deleted test job: {j.id}")
            except Exception as e:
                print(f"  -> Error deleting test job {j.id}: {e}")
                
        if test_video:
            try:
                video_repo.delete(test_video.id)
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
        print("--- JobService Tests Complete ---")

if __name__ == "__main__":
    run_job_service_tests()
