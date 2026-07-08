import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import Depends
from fastapi.testclient import TestClient
from backend.main import app
from backend.api.pipeline_dependencies import get_video_worker_dependency
from backend.providers.text.dependency import get_text_provider
from backend.providers.text.fake import FakeTextGenerationProvider
from backend.providers.audio.dependency import get_audio_provider
from backend.providers.audio.fake import FakeAudioGenerationProvider
from backend.providers.image.dependency import get_image_provider
from backend.providers.image.fake import FakeImageGenerationProvider
from backend.workers.video_worker import VideoWorker
from backend.services.pipeline_service import PipelineService
from backend.services.video_service import VideoService
from backend.services.audio_service import AudioService
from backend.services.image_service import ImageService
from backend.services.job_service import JobService
from backend.config.session import get_db

@app.get("/test-pipeline-dependency-identity")
def test_pipeline_dependency_identity(
    worker: VideoWorker = Depends(get_video_worker_dependency),
    db = Depends(get_db)
):
    pipeline = worker.pipeline_service
    vs = pipeline.video_service
    ast = pipeline.audio_service
    ist = pipeline.image_service
    js = worker.job_service
    
    return {
        "is_worker": isinstance(worker, VideoWorker),
        "is_pipeline": isinstance(pipeline, PipelineService),
        "is_vs": isinstance(vs, VideoService),
        "is_ast": isinstance(ast, AudioService),
        "is_ist": isinstance(ist, ImageService),
        "db_match_vs": js.db is vs.db,
        "db_match_ast": js.db is ast.db,
        "db_match_ist": js.db is ist.db,
        "vs_provider_is_fake": isinstance(vs.text_provider, FakeTextGenerationProvider),
        "ast_provider_is_fake": isinstance(ast.audio_provider, FakeAudioGenerationProvider),
        "ist_provider_is_fake": isinstance(ist.image_provider, FakeImageGenerationProvider),
    }

def run_tests():
    print("--- Pipeline Dependency Identity Test ---")
    
    # Override
    fake_text = FakeTextGenerationProvider()
    fake_audio = FakeAudioGenerationProvider()
    fake_image = FakeImageGenerationProvider()
    
    app.dependency_overrides[get_text_provider] = lambda: fake_text
    app.dependency_overrides[get_audio_provider] = lambda: fake_audio
    app.dependency_overrides[get_image_provider] = lambda: fake_image
    
    client = TestClient(app)
    
    try:
        response = client.get("/test-pipeline-dependency-identity")
        response.raise_for_status()
        data = response.json()
        
        for k, v in data.items():
            if not v:
                raise AssertionError(f"Identity assertion failed for {k}")
                
        print("  -> PASS: All dependency identities match exactly.")
    finally:
        app.dependency_overrides.clear()
        
    print("--- Test Complete ---")

if __name__ == "__main__":
    run_tests()
