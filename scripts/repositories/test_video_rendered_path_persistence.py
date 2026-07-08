import sys
import os
import uuid
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.database import engine
from backend.models.base import Base
from backend.config.session import SessionLocal
from backend.repositories.channel_repository import ChannelRepository
from backend.repositories.video_repository import VideoRepository

def run_tests():
    print("--- Starting Video Rendered Path Persistence Tests ---")
    
    Base.metadata.create_all(bind=engine)
    
    # Session 1
    db1 = SessionLocal()
    channel_repo1 = ChannelRepository(db1)
    video_repo1 = VideoRepository(db1)
    
    test_channel = None
    test_video = None
    
    try:
        print("\n[Setup] Creating temporary test channel...")
        test_channel = channel_repo1.create({
            "name": f"Render Path Persistence Test {uuid.uuid4().hex[:8]}",
            "niche": "Testing",
            "youtube_account": f"render_test_{uuid.uuid4().hex[:8]}",
            "is_active": True
        })
        
        print("\n[Test 1] Create Video")
        test_video = video_repo1.create({
            "channel_id": test_channel.id,
            "topic": "Testing rendered_video_path persistence"
        })
        video_id = test_video.id
        print("  -> PASS: Video created successfully.")
        
        print("\n[Test 2] Initial Value")
        if test_video.rendered_video_path is not None:
            raise AssertionError(f"Expected None, got {test_video.rendered_video_path}")
        print("  -> PASS: Initial value is None.")
        
        print("\n[Test 3] Update through generic repository method")
        expected_render_path = f"storage/videos/{video_id}/final.fake"
        expected_audio_path = f"storage/videos/{video_id}/audio.fake"
        
        # Update both to also test independence
        updated_video = video_repo1.update(
            video_id,
            {
                "rendered_video_path": expected_render_path,
                "audio_path": expected_audio_path
            }
        )
        if updated_video.rendered_video_path != expected_render_path:
            raise AssertionError(f"Expected {expected_render_path}, got {updated_video.rendered_video_path}")
        print("  -> PASS: Memory object updated successfully.")
        
        print("\n[Test 4] Same-session fetch")
        same_session_video = video_repo1.get_by_id(video_id)
        if same_session_video.rendered_video_path != expected_render_path:
            raise AssertionError(f"Expected {expected_render_path}, got {same_session_video.rendered_video_path}")
        print("  -> PASS: Fetched correctly within same session.")
        
        # Close first session
        db1.close()
        
        print("\n[Test 5] Cross-session persistence")
        # Session 2
        db2 = SessionLocal()
        try:
            video_repo2 = VideoRepository(db2)
            persisted_video = video_repo2.get_by_id(video_id)
            
            if persisted_video.rendered_video_path != expected_render_path:
                raise AssertionError(f"Cross-session persistence failed. Expected {expected_render_path}, got {persisted_video.rendered_video_path}")
            print("  -> PASS: Rendered video path persisted successfully across sessions.")
            
            print("\n[Test 6] Audio Path Independence")
            if persisted_video.audio_path != expected_audio_path:
                raise AssertionError("Audio path persistence broke.")
            
            # Update only rendered path
            new_render_path = f"storage/videos/{video_id}/final2.fake"
            video_repo2.update(
                video_id,
                {"rendered_video_path": new_render_path}
            )
            
            db2.close()
            
            # Session 3
            db3 = SessionLocal()
            try:
                video_repo3 = VideoRepository(db3)
                final_video = video_repo3.get_by_id(video_id)
                if final_video.rendered_video_path != new_render_path:
                    raise AssertionError("Second update failed")
                if final_video.audio_path != expected_audio_path:
                    raise AssertionError("Updating rendered path cleared audio path")
                print("  -> PASS: Fields are completely independent.")
                
                print("\n[Test 7] Nullability Reset")
                video_repo3.update(
                    video_id,
                    {"rendered_video_path": None}
                )
                
                db3.close()
                
                # Session 4
                db4 = SessionLocal()
                try:
                    video_repo4 = VideoRepository(db4)
                    null_video = video_repo4.get_by_id(video_id)
                    if null_video.rendered_video_path is not None:
                        raise AssertionError("Failed to reset to None")
                    print("  -> PASS: Successfully reset to None.")
                finally:
                    db4.close()
                    
            finally:
                if 'db3' in locals():
                    db3.close()
                    
        finally:
            if 'db2' in locals():
                db2.close()
        
    except Exception:
        print("\n--- UNEXPECTED CRITICAL ERROR ---")
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        print("\n[Cleanup] Removing temporary database records...")
        # Use a fresh session for cleanup just to be safe
        cleanup_db = SessionLocal()
        try:
            cleanup_video_repo = VideoRepository(cleanup_db)
            cleanup_channel_repo = ChannelRepository(cleanup_db)
            
            if test_video:
                cleanup_video_repo.delete(test_video.id)
            if test_channel:
                cleanup_channel_repo.delete(test_channel.id)
        except Exception as e:
            print(f"Cleanup error (safe to ignore if records don't exist): {e}")
        finally:
            cleanup_db.close()
            
    print("\n--- All Video Rendered Path Persistence Tests Passed! ---")

if __name__ == "__main__":
    run_tests()
