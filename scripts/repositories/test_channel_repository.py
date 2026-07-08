import sys
import os

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.config.session import SessionLocal
from backend.repositories.channel_repository import ChannelRepository
from backend.models.base import Base
from backend.config.database import engine
from backend.models.channel import Channel
from backend.models.video import Video

def run_repository_tests():
    # Ensure tables are created before testing
    Base.metadata.create_all(bind=engine)
    
    # 1. Create a database session
    db = SessionLocal()
    
    # 2. Create ChannelRepository
    repo = ChannelRepository(db)
    
    try:
        print("--- Starting ChannelRepository Tests ---")
        
        # 3. Create a test channel
        channel_data = {
            "name": "Test Repository Channel",
            "niche": "Automated Testing",
            "youtube_account": "test_account_123"
        }
        created_channel = repo.create(channel_data)
        channel_id = created_channel.id
        print(f"[Create] Successfully created channel with ID: {channel_id}")
        
        # 4. Fetch the channel
        fetched_channel = repo.get_by_id(channel_id)
        if fetched_channel:
            print(f"[Fetch] Successfully retrieved channel: '{fetched_channel.name}' (Niche: {fetched_channel.niche})")
        else:
            print("[Fetch] Error: Failed to retrieve the newly created channel.")
            
        # 5. Update the channel
        update_data = {"is_active": False, "name": "Updated Repo Channel"}
        updated_channel = repo.update(channel_id, update_data)
        print(f"[Update] Successfully updated channel. New Name: '{updated_channel.name}', is_active: {updated_channel.is_active}")
        
        # 6. Delete the channel
        delete_success = repo.delete(channel_id)
        if delete_success:
            print(f"[Delete] Successfully deleted channel with ID: {channel_id}")
            
        # Verify deletion
        verify_deleted = repo.get_by_id(channel_id)
        if not verify_deleted:
            print("[Verify] Confirmed that the channel no longer exists in the database.")
        else:
            print("[Verify] Error: Channel still exists after deletion!")
            
        print("--- All repository tests completed successfully ---")

    except Exception as e:
        print(f"Error during repository testing: {e}")
        
    finally:
        # Close the session
        db.close()

if __name__ == "__main__":
    run_repository_tests()
