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
from backend.workers.video_worker import VideoWorker

class SuccessfulPipelineStub:
    def __init__(self):
        self.received_video_id = None
        
    def process_video(self, video_id: uuid.UUID, progress_callback=None):
        self.received_video_id = video_id
        if progress_callback:
            progress_callback(10, "Generating Text")
            progress_callback(40, "Text Generated")
            progress_callback(50, "Generating Audio")
            progress_callback(90, "Audio Generated")

class FailingPipelineStub:
    def __init__(self):
        self.received_video_id = None
        
    def process_video(self, video_id: uuid.UUID, progress_callback=None):
        self.received_video_id = video_id
        if progress_callback:
            progress_callback(10, "Generating Text")
        raise ValueError("Simulated pipeline failure")

def run_worker_tests():
    print("--- Starting VideoWorker Integration Tests ---")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    channel_repo = ChannelRepository(db)
    video_repo = VideoRepository(db)
    job_service = JobService(db)
    
    test_channel = None
    test_video = None
    created_jobs = []
    
    try:
        # Setup
        print("\n[Setup] Creating temporary test channel, video, and job...")
        test_channel = channel_repo.create({
            "name": "Worker Test Channel",
            "niche": "Testing",
            "youtube_account": "worker_test_123",
            "is_active": True
        })
        test_video = video_repo.create({
            "channel_id": test_channel.id,
            "topic": "Worker Test Topic"
        })
        job1 = job_service.create_job(test_video.id)
        created_jobs.append(job1)
        
        # TEST 1
        print("\n[Test 1] Successful worker execution")
        if job1.status != JobStatus.QUEUED: raise AssertionError("Job not initially QUEUED")
        
        success_stub = SuccessfulPipelineStub()
        worker_success = VideoWorker(job_service=job_service, pipeline_service=success_stub)
        
        completed_job = worker_success.execute(job1.id)
        
        if completed_job.status != JobStatus.COMPLETED: raise AssertionError("Job not COMPLETED")
        if completed_job.progress != 100: raise AssertionError("Progress != 100")
        if completed_job.current_step != "Completed": raise AssertionError("current_step mismatch")
        if completed_job.started_at is None: raise AssertionError("started_at None")
        if completed_job.finished_at is None: raise AssertionError("finished_at None")
        if completed_job.error is not None: raise AssertionError("error not None")
        if success_stub.received_video_id != test_video.id: raise AssertionError("Pipeline stub didn't receive correct video_id")
        
        refetched_job = job_service.get_job(job1.id)
        if refetched_job.status != JobStatus.COMPLETED: raise AssertionError("COMPLETED state not persisted")
        
        # TEST 2
        print("\n[Test 2] Retry setup after completed job")
        job2 = job_service.create_job(test_video.id)
        created_jobs.append(job2)
        if job2.status != JobStatus.QUEUED: raise AssertionError("Second job not QUEUED")
        
        # TEST 3
        print("\n[Test 3] Failed worker execution")
        fail_stub = FailingPipelineStub()
        worker_fail = VideoWorker(job_service=job_service, pipeline_service=fail_stub)
        
        try:
            worker_fail.execute(job2.id)
            raise AssertionError("Worker did not re-raise pipeline exception")
        except Exception as e:
            if not isinstance(e, ValueError): raise AssertionError("Wrong exception type")
            if str(e) != "Simulated pipeline failure": raise AssertionError("Wrong exception message")
            
        if fail_stub.received_video_id != test_video.id: raise AssertionError("Pipeline stub didn't receive correct video_id")
        
        refetched_job2 = job_service.get_job(job2.id)
        if refetched_job2.status != JobStatus.FAILED: raise AssertionError("FAILED state not persisted")
        if refetched_job2.started_at is None: raise AssertionError("started_at None")
        if refetched_job2.finished_at is None: raise AssertionError("finished_at None")
        if refetched_job2.error != "Simulated pipeline failure": raise AssertionError("Error message not persisted")
        if refetched_job2.progress != 10: raise AssertionError("Progress should be 10 on failure")
        if refetched_job2.current_step != "Generating Text": raise AssertionError("current_step should be Generating Text")
        
        # TEST 4
        print("\n[Test 4] New retry allowed after failed job")
        job3 = job_service.create_job(test_video.id)
        created_jobs.append(job3)
        if job3.status != JobStatus.QUEUED: raise AssertionError("Third job not QUEUED")
        
        # TEST 5
        print("\n[Test 5] Worker rejects missing Job")
        fail_stub2 = FailingPipelineStub()
        worker_missing = VideoWorker(job_service=job_service, pipeline_service=fail_stub2)
        
        try:
            worker_missing.execute(uuid.uuid4())
            raise AssertionError("Allowed execute for missing job")
        except ValueError as e:
            if str(e) != "Job not found": raise AssertionError("Wrong error message")
            
        if fail_stub2.received_video_id is not None: raise AssertionError("Pipeline stub should not be called")
        
        # TEST 6
        print("\n[Test 6] Invalid worker execution state")
        job_service.start_job(job3.id)
        job3_started = job_service.get_job(job3.id)
        if job3_started.status != JobStatus.RUNNING: raise AssertionError("Third job not RUNNING")
        
        fail_stub3 = FailingPipelineStub()
        worker_invalid = VideoWorker(job_service=job_service, pipeline_service=fail_stub3)
        
        try:
            worker_invalid.execute(job3.id)
            raise AssertionError("Allowed execute for RUNNING job")
        except ValueError as e:
            if "Invalid job status transition" not in str(e): raise AssertionError("Wrong error message")
            
        if fail_stub3.received_video_id is not None: raise AssertionError("Pipeline stub should not be called")
        
    except Exception:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        sys.exit(1)
        
    finally:
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
        print("--- VideoWorker Tests Complete ---")

if __name__ == "__main__":
    run_worker_tests()
