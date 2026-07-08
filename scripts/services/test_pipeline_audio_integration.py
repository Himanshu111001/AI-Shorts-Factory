import sys
import os
import uuid
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.pipeline_service import PipelineService
from backend.services.pipeline_dependency import get_pipeline_service

class RecordingVideoService:
    def __init__(self, call_order):
        self.call_order = call_order
        
    def generate_text_content(self, video_id):
        self.call_order.append("text")
        return "final_video_sentinel"

class RecordingAudioService:
    def __init__(self, call_order):
        self.call_order = call_order
        
    def generate_audio(self, video_id):
        if "text" not in self.call_order:
            raise AssertionError("text was not in call order")
        self.call_order.append("audio")
        return "final_video_sentinel"

class RecordingImageService:
    def __init__(self, call_order, expected_video_id):
        self.call_order = call_order
        self.expected_video_id = expected_video_id
        
    def generate_images(self, video_id):
        if video_id != self.expected_video_id:
            raise AssertionError("Mismatch video_id in ImageService")
        if "audio" not in self.call_order:
            raise AssertionError("audio was not in call order")
        self.call_order.append("image")
        return ["img1", "img2"]

class FailingVideoService:
    def generate_text_content(self, video_id):
        raise ValueError("Simulated text failure")

class FailingAudioService:
    def __init__(self, call_order):
        self.call_order = call_order
        
    def generate_audio(self, video_id):
        if "text" not in self.call_order:
            raise AssertionError("text was not in call order")
        self.call_order.append("audio")
        raise ValueError("Simulated audio failure")

class FailingImageService:
    def __init__(self, call_order):
        self.call_order = call_order
        
    def generate_images(self, video_id):
        if "audio" not in self.call_order:
            raise AssertionError("audio was not in call order")
        self.call_order.append("image")
        raise ValueError("Simulated image failure")

def run_tests():
    print("--- Pipeline Integration Tests ---")
    
    vid = uuid.uuid4()
    
    print("\n[Test 1] Order verification")
    call_order = []
    progress_calls = []
    
    def mock_callback(progress, step):
        progress_calls.append((progress, step))

    vs = RecordingVideoService(call_order)
    ast = RecordingAudioService(call_order)
    ist = RecordingImageService(call_order, vid)
    pipeline = PipelineService(video_service=vs, audio_service=ast, image_service=ist)
    
    res = pipeline.process_video(vid, progress_callback=mock_callback)
    if call_order != ["text", "audio", "image"]: raise AssertionError(f"Wrong order: {call_order}")
    if res != "final_video_sentinel": raise AssertionError(f"Wrong return: {res}")
    
    expected_progress = [
        (10, "Generating Text"),
        (35, "Text Generated"),
        (40, "Generating Audio"),
        (60, "Audio Generated"),
        (65, "Generating Images"),
        (90, "Images Generated")
    ]
    if progress_calls != expected_progress: raise AssertionError(f"Wrong progress sequence: {progress_calls}")
    
    print("\n[Test 2] Failure Short-circuiting (Text Failure)")
    progress_calls.clear()
    vs_fail = FailingVideoService()
    ast_record = RecordingAudioService([])
    ist_record = RecordingImageService([], vid)
    pipeline_fail_text = PipelineService(video_service=vs_fail, audio_service=ast_record, image_service=ist_record)
    try:
        pipeline_fail_text.process_video(vid, progress_callback=mock_callback)
        raise AssertionError("Did not propagate")
    except ValueError as e:
        if str(e) != "Simulated text failure": raise AssertionError(f"Wrong error: {e}")
    if len(ast_record.call_order) > 0: raise AssertionError("Audio service called when text failed")
    if len(ist_record.call_order) > 0: raise AssertionError("Image service called when text failed")
    if progress_calls[-1] != (10, "Generating Text"): raise AssertionError(f"Wrong progress state: {progress_calls}")
        
    print("\n[Test 3] Audio Failure Propagation")
    progress_calls.clear()
    call_order = []
    vs2 = RecordingVideoService(call_order)
    ast_fail = FailingAudioService(call_order)
    ist_record2 = RecordingImageService([], vid)
    pipeline_fail_audio = PipelineService(video_service=vs2, audio_service=ast_fail, image_service=ist_record2)
    try:
        pipeline_fail_audio.process_video(vid, progress_callback=mock_callback)
        raise AssertionError("Did not propagate")
    except ValueError as e:
        if str(e) != "Simulated audio failure": raise AssertionError(f"Wrong error: {e}")
    if call_order != ["text", "audio"]: raise AssertionError(f"Wrong order: {call_order}")
    if len(ist_record2.call_order) > 0: raise AssertionError("Image service called when audio failed")
    if progress_calls[-1] != (40, "Generating Audio"): raise AssertionError(f"Wrong progress state: {progress_calls}")
    
    print("\n[Test 4] Image Failure Propagation")
    progress_calls.clear()
    call_order = []
    vs3 = RecordingVideoService(call_order)
    ast3 = RecordingAudioService(call_order)
    ist_fail = FailingImageService(call_order)
    pipeline_fail_image = PipelineService(video_service=vs3, audio_service=ast3, image_service=ist_fail)
    try:
        pipeline_fail_image.process_video(vid, progress_callback=mock_callback)
        raise AssertionError("Did not propagate")
    except ValueError as e:
        if str(e) != "Simulated image failure": raise AssertionError(f"Wrong error: {e}")
    if call_order != ["text", "audio", "image"]: raise AssertionError(f"Wrong order: {call_order}")
    if progress_calls[-1] != (65, "Generating Images"): raise AssertionError(f"Wrong progress state: {progress_calls}")
    
    print("\n[Test 5] Dependency constructor")
    obj_vs = object()
    obj_ast = object()
    obj_ist = object()
    constructed = get_pipeline_service(video_service=obj_vs, audio_service=obj_ast, image_service=obj_ist)
    if constructed.video_service is not obj_vs: raise AssertionError("Mismatch video_service")
    if constructed.audio_service is not obj_ast: raise AssertionError("Mismatch audio_service")
    if constructed.image_service is not obj_ist: raise AssertionError("Mismatch image_service")
    
    print("\n--- Pipeline Order Verification Passed ---")

if __name__ == "__main__":
    run_tests()
