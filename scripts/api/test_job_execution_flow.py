import sys
import os
import uuid
import traceback
import tempfile
import shutil
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi.testclient import TestClient

from backend.main import app
from backend.config.database import engine
from backend.models.base import Base
from backend.config.session import SessionLocal
from backend.repositories.channel_repository import ChannelRepository
from backend.repositories.video_repository import VideoRepository
from backend.repositories.job_repository import JobRepository
from backend.providers.text.dependency import get_text_provider
from backend.providers.text.fake import FakeTextGenerationProvider
from backend.providers.text.base import TextGenerationProvider
from backend.providers.audio.dependency import get_audio_provider
from backend.providers.audio.fake import FakeAudioGenerationProvider
from backend.providers.audio.base import AudioGenerationProvider
from backend.providers.image.dependency import get_image_provider
from backend.providers.image.fake import FakeImageGenerationProvider
from backend.providers.image.base import ImageGenerationProvider
from backend.providers.render.dependency import get_render_provider
from backend.providers.render.fake import FakeRenderProvider
from backend.providers.render.base import RenderProvider
from backend.repositories.generated_image_repository import GeneratedImageRepository
from backend.models.enums.job_status import JobStatus
from backend.models.enums.video_status import VideoStatus
from backend.config.settings import get_settings

def run_tests():
    print("--- Starting Complete Job Execution Flow Integration Tests ---")
    
    # Storage isolation
    original_storage_path = os.environ.get("STORAGE_PATH")
    test_storage_dir = tempfile.mkdtemp(prefix="aimf_api_flow_test_")
    os.environ["STORAGE_PATH"] = test_storage_dir
    get_settings.cache_clear()

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    
    fake_text_provider = FakeTextGenerationProvider()
    fake_audio_provider = FakeAudioGenerationProvider()
    fake_image_provider = FakeImageGenerationProvider()
    fake_render_provider = FakeRenderProvider()
    
    app.dependency_overrides[get_text_provider] = lambda: fake_text_provider
    app.dependency_overrides[get_audio_provider] = lambda: fake_audio_provider
    app.dependency_overrides[get_image_provider] = lambda: fake_image_provider
    app.dependency_overrides[get_render_provider] = lambda: fake_render_provider
    
    client = TestClient(app)
    db = SessionLocal()
    
    channel_repo = ChannelRepository(db)
    video_repo = VideoRepository(db)
    job_repo = JobRepository(db)
    img_repo = GeneratedImageRepository(db)
    
    test_channel = None
    created_video_ids = []
    created_job_ids = []
    
    try:
        print("\n[Setup] Creating temporary active channel...")
        channel_name = f"API Flow Test Channel {uuid.uuid4().hex[:8]}"
        niche = "Automation Testing"
        test_channel = channel_repo.create({
            "name": channel_name,
            "niche": niche,
            "youtube_account": f"api_test_{uuid.uuid4().hex[:8]}",
            "is_active": True
        })
        channel_id_str = str(test_channel.id)

        # SUCCESS FLOW
        # TEST 1
        print("\n[Test 1] Create Video through API")
        topic = "End to End API Execution"
        response = client.post(
            "/videos/",
            json={"channel_id": channel_id_str, "topic": topic}
        )
        if response.status_code != 201:
            raise AssertionError(f"Expected 201, got {response.status_code}. Resp: {response.text}")
        
        video1_data = response.json()
        video1_id = video1_data["id"]
        created_video_ids.append(video1_id)
        
        if video1_data["channel_id"] != channel_id_str: raise AssertionError("Channel mismatch")
        if video1_data["topic"] != topic: raise AssertionError("Topic mismatch")
        if video1_data["status"] != "CREATED": raise AssertionError("Status not CREATED")
        
        # TEST 2
        print("\n[Test 2] Transition Video to PROCESSING")
        response = client.patch(
            f"/videos/{video1_id}/status",
            json={"status": "PROCESSING"}
        )
        if response.status_code != 200:
            raise AssertionError(f"Expected 200, got {response.status_code}. Resp: {response.text}")
        if response.json()["status"] != "PROCESSING": raise AssertionError("Status not PROCESSING")
        
        # TEST 3
        print("\n[Test 3] Create QUEUED Job")
        response = client.post(f"/jobs/video/{video1_id}")
        if response.status_code != 201:
            raise AssertionError(f"Expected 201, got {response.status_code}. Resp: {response.text}")
        job1_data = response.json()
        job1_id = job1_data["id"]
        created_job_ids.append(job1_id)
        
        if job1_data["video_id"] != video1_id: raise AssertionError("Video ID mismatch")
        if job1_data["status"] != "QUEUED": raise AssertionError("Job not QUEUED")
        if job1_data["progress"] != 0: raise AssertionError("Progress not 0")
        
        # TEST 4
        print("\n[Test 4] Execute Job through synchronous API")
        response = client.post(f"/jobs/{job1_id}/execute")
        if response.status_code != 200:
            raise AssertionError(f"Expected 200, got {response.status_code}. Resp: {response.text}")
        
        job1_exec_data = response.json()
        if job1_exec_data["id"] != job1_id: raise AssertionError("ID mismatch")
        if job1_exec_data["status"] != "COMPLETED": raise AssertionError("Job not COMPLETED")
        if job1_exec_data["progress"] != 100: raise AssertionError("Progress not 100")
        
        # TEST 5
        print("\n[Test 5] Verify generated Video content through API")
        response = client.get(f"/videos/{video1_id}")
        if response.status_code != 200:
            raise AssertionError(f"Expected 200, got {response.status_code}")
            
        video_fetched = response.json()
        
        expected_title = fake_text_provider.generate_title(topic, niche)
        expected_desc = fake_text_provider.generate_description(topic, expected_title, niche)
        expected_script = fake_text_provider.generate_script(topic, expected_title, niche)
        expected_hashtags = fake_text_provider.generate_hashtags(topic, expected_title, niche)
        
        if video_fetched["title"] != expected_title: raise AssertionError("Title mismatch")
        if video_fetched["description"] != expected_desc: raise AssertionError("Desc mismatch")
        if video_fetched["script"] != expected_script: raise AssertionError("Script mismatch")
        if video_fetched["hashtags"] != expected_hashtags: raise AssertionError("Hashtags mismatch")
        if video_fetched["audio_path"] is None: raise AssertionError("audio_path is None")
        if video_fetched["rendered_video_path"] is None: raise AssertionError("rendered_video_path is None")
        
        if not os.path.exists(video_fetched["audio_path"]):
            raise AssertionError("Generated audio artifact does not exist on filesystem")
            
        with open(video_fetched["audio_path"], "r", encoding="utf-8") as f:
            audio_content = f.read()
        expected_audio_content = f"FAKE_AUDIO_ARTIFACT\nTEXT_LENGTH:{len(expected_script)}\nTEXT:{expected_script.strip()}"
        if audio_content != expected_audio_content:
            raise AssertionError(f"Audio content mismatch. Expected: {expected_audio_content}, Got: {audio_content}")
            
        if not os.path.exists(video_fetched["rendered_video_path"]):
            raise AssertionError("Generated render artifact does not exist on filesystem")
        
        db.expire_all()
        images = img_repo.get_by_video_id(uuid.UUID(video1_id))
            
        with open(video_fetched["rendered_video_path"], "r", encoding="utf-8") as f:
            render_content = f.read().splitlines()
        
        if render_content[0] != "FAKE_RENDER_ARTIFACT": raise AssertionError("Render artifact header mismatch")
        if render_content[1] != f"AUDIO_PATH:{video_fetched['audio_path']}": raise AssertionError("Render artifact audio path mismatch")
        if render_content[2] != f"IMAGE_COUNT:{len(images)}": raise AssertionError("Render artifact image count mismatch")
        
        for i, img in enumerate(images, 1):
            if render_content[i+2] != f"IMAGE_{i:03d}:{img.file_path}":
                raise AssertionError(f"Render artifact image path mismatch for image {i}")

        if video_fetched["status"] != "PROCESSING": raise AssertionError("Video status not PROCESSING")
        
        # TEST 6
        print("\n[Test 6] Verify direct database persistence")
        db.expire_all()
        db_video = video_repo.get_by_id(uuid.UUID(video1_id))
        
        if db_video.title != expected_title: raise AssertionError("DB Title mismatch")
        if db_video.script != expected_script: raise AssertionError("DB Script mismatch")
        if db_video.audio_path is None: raise AssertionError("DB audio_path is None")
        if not os.path.exists(db_video.audio_path): raise AssertionError("DB audio_path file missing")
        if db_video.rendered_video_path is None: raise AssertionError("DB rendered_video_path is None")
        if not os.path.exists(db_video.rendered_video_path): raise AssertionError("DB rendered_video_path file missing")
        
        db_job = job_repo.get_by_id(uuid.UUID(job1_id))
        if db_job.status != JobStatus.COMPLETED: raise AssertionError("DB Job status not COMPLETED")
        if db_job.progress != 100: raise AssertionError("DB Job progress not 100")

        print("\n[Test 6.5] Verify GeneratedImage direct database persistence")
        images = img_repo.get_by_video_id(uuid.UUID(video1_id))
        if not images: raise AssertionError("No images persisted in DB")
        seqs = [i.sequence_index for i in images]
        if seqs != list(range(1, len(images) + 1)): raise AssertionError("Images not sequentially ordered")
        for i in images:
            if not i.prompt: raise AssertionError("Missing image prompt")
            if not i.file_path: raise AssertionError("Missing image file_path")
            if not os.path.exists(i.file_path): raise AssertionError(f"Image fake artifact missing: {i.file_path}")

        # TEST 7
        print("\n[Test 7] Reject completed Job re-execution")
        response = client.post(f"/jobs/{job1_id}/execute")
        if response.status_code != 409: raise AssertionError(f"Expected 409, got {response.status_code}")
            
        db.expire_all()
        db_job = job_repo.get_by_id(uuid.UUID(job1_id))
        if db_job.status != JobStatus.COMPLETED: raise AssertionError("Status mutated on re-execution")
        if db_job.progress != 100: raise AssertionError("Progress mutated on re-execution")

        # FAILURE FLOW
        print("\n[Failure Flow Setup] Creating CREATED Video and QUEUED Job...")
        topic2 = "Failure flow test"
        response = client.post(
            "/videos/",
            json={"channel_id": channel_id_str, "topic": topic2}
        )
        video2_id = response.json()["id"]
        created_video_ids.append(video2_id)
        
        response = client.post(f"/jobs/video/{video2_id}")
        job2_id = response.json()["id"]
        created_job_ids.append(job2_id)

        # TEST 8
        print("\n[Test 8] Execute Job against invalid Video state")
        response = client.post(f"/jobs/{job2_id}/execute")
        if response.status_code != 400: raise AssertionError(f"Expected 400, got {response.status_code}")
        if "Text generation requires PROCESSING status" not in response.json()["detail"]:
            raise AssertionError("Wrong detail error")
            
        # TEST 9
        print("\n[Test 9] Verify FAILED Job persistence")
        db.expire_all()
        db_job2 = job_repo.get_by_id(uuid.UUID(job2_id))
        if db_job2.status != JobStatus.FAILED: raise AssertionError("Job status not FAILED")
        if db_job2.progress != 10: raise AssertionError("Job progress not 10")
        if db_job2.current_step != "Generating Text": raise AssertionError("Job current_step not Generating Text")
        if "Text generation requires PROCESSING status" not in db_job2.error: raise AssertionError("Job error mismatch")

        # TEST 10
        print("\n[Test 10] Verify failed Video was not mutated")
        db_video2 = video_repo.get_by_id(uuid.UUID(video2_id))
        if db_video2.status != VideoStatus.CREATED: raise AssertionError("Video mutated from CREATED")
        if db_video2.title is not None: raise AssertionError("Video title was mutated")
        if db_video2.audio_path is not None: raise AssertionError("Video audio_path was mutated")
        expected_missing_dir = os.path.join(test_storage_dir, "videos", str(db_video2.id))
        if os.path.exists(expected_missing_dir): raise AssertionError("Audio directory was created despite failure")

        # IMAGE FAILURE FLOW
        print("\n[Failure Flow Setup] Creating CREATED Video and QUEUED Job for Image failure...")
        topic3 = "Image failure flow test"
        response = client.post(
            "/videos/",
            json={"channel_id": channel_id_str, "topic": topic3}
        )
        video3_id = response.json()["id"]
        created_video_ids.append(video3_id)
        client.patch(f"/videos/{video3_id}/status", json={"status": "PROCESSING"})
        
        response = client.post(f"/jobs/video/{video3_id}")
        job3_id = response.json()["id"]
        created_job_ids.append(job3_id)

        class FailingImageProvider(ImageGenerationProvider):
            def generate_images(self, prompts, output_dir):
                raise ValueError("Simulated image failure during execution")

        app.dependency_overrides[get_image_provider] = lambda: FailingImageProvider()
        
        print("\n[Test 11] Execute Job expecting Image failure")
        response = client.post(f"/jobs/{job3_id}/execute")
        if response.status_code != 500: raise AssertionError(f"Expected 500, got {response.status_code}")
        if "Job execution failed" not in response.json()["detail"]:
            raise AssertionError("Wrong detail error for image failure")
            
        print("\n[Test 12] Verify FAILED Job persistence after Image failure")
        db.expire_all()
        db_job3 = job_repo.get_by_id(uuid.UUID(job3_id))
        if db_job3.status != JobStatus.FAILED: raise AssertionError("Job status not FAILED")
        if db_job3.progress != 55: raise AssertionError(f"Job progress not 55, got {db_job3.progress}")
        if db_job3.current_step != "Generating Images": raise AssertionError("Job current_step not Generating Images")
        
        db_video3 = video_repo.get_by_id(uuid.UUID(video3_id))
        if db_video3.title is None: raise AssertionError("Video title was lost")
        if db_video3.audio_path is None: raise AssertionError("Video audio_path was lost")
        
        img_check = img_repo.get_by_video_id(uuid.UUID(video3_id))
        if len(img_check) > 0: raise AssertionError("Images were persisted despite failure")
        
        # RENDER FAILURE FLOW
        print("\n[Failure Flow Setup] Creating CREATED Video and QUEUED Job for Render failure...")
        topic4 = "Render failure flow test"
        response = client.post(
            "/videos/",
            json={"channel_id": channel_id_str, "topic": topic4}
        )
        video4_id = response.json()["id"]
        created_video_ids.append(video4_id)
        client.patch(f"/videos/{video4_id}/status", json={"status": "PROCESSING"})
        
        response = client.post(f"/jobs/video/{video4_id}")
        job4_id = response.json()["id"]
        created_job_ids.append(job4_id)
        
        # Restore normal image provider for this test
        app.dependency_overrides[get_image_provider] = lambda: fake_image_provider

        class FailingRenderProvider(RenderProvider):
            def render_video(self, audio_path, image_paths, output_path):
                raise ValueError("Simulated render failure during execution")

        app.dependency_overrides[get_render_provider] = lambda: FailingRenderProvider()
        
        print("\n[Test 13] Execute Job expecting Render failure")
        response = client.post(f"/jobs/{job4_id}/execute")
        if response.status_code != 500: raise AssertionError(f"Expected 500, got {response.status_code}")
        if "Job execution failed" not in response.json()["detail"]:
            raise AssertionError("Wrong detail error for render failure")
            
        print("\n[Test 14] Verify FAILED Job persistence after Render failure")
        db.expire_all()
        db_job4 = job_repo.get_by_id(uuid.UUID(job4_id))
        if db_job4.status != JobStatus.FAILED: raise AssertionError("Job status not FAILED")
        if db_job4.progress != 80: raise AssertionError(f"Job progress not 80, got {db_job4.progress}")
        if db_job4.current_step != "Rendering Video": raise AssertionError("Job current_step not Rendering Video")
        if "Simulated render failure during execution" not in db_job4.error: raise AssertionError("Render error message not persisted")
        
        db_video4 = video_repo.get_by_id(uuid.UUID(video4_id))
        if db_video4.title is None: raise AssertionError("Video title was lost")
        if db_video4.audio_path is None: raise AssertionError("Video audio_path was lost")
        if db_video4.rendered_video_path is not None: raise AssertionError("Video rendered_video_path should be None after render failure")
        
        img_check4 = img_repo.get_by_video_id(uuid.UUID(video4_id))
        if len(img_check4) == 0: raise AssertionError("Images were NOT persisted despite render failure")

    except Exception:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        print("\n[Cleanup] Removing temporary database records...")
        for j_id in created_job_ids:
            try:
                job_repo.delete(uuid.UUID(j_id))
            except Exception as e:
                pass
                
        for v_id in created_video_ids:
            try:
                img_repo.delete_by_video_id(uuid.UUID(v_id))
            except Exception:
                pass
            try:
                video_repo.delete(uuid.UUID(v_id))
            except Exception as e:
                pass
                
        if test_channel:
            try:
                channel_repo.delete(test_channel.id)
            except Exception as e:
                pass
                
        db.close()
        app.dependency_overrides.clear()
        
        shutil.rmtree(test_storage_dir, ignore_errors=True)
        if original_storage_path is not None:
            os.environ["STORAGE_PATH"] = original_storage_path
        else:
            if "STORAGE_PATH" in os.environ:
                del os.environ["STORAGE_PATH"]
        get_settings.cache_clear()
        
    print("\n--- All tests passed! Complete synchronous Job execution flow works as expected. ---")

if __name__ == "__main__":
    run_tests()
