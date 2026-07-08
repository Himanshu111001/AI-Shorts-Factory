import sys
import os

# Ensure the root project directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy import inspect
from backend.config.database import engine
from backend.models.base import Base
# We must import the Channel model so that Base metadata knows about it
from backend.models.channel import Channel
from backend.models.video import Video

def verify_database():
    try:
        print("Initializing database connection...")
        
        # This will create aimf.db if it doesn't exist, and create the channels table
        Base.metadata.create_all(bind=engine)
        
        # Verify connection by inspecting the database
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if "channels" in tables:
            print(f"Success! Database connection verified.")
            print(f"Tables successfully created: {tables}")
        else:
            print("Error: The 'channels' table was not found after creation.")
            
    except Exception as e:
        print(f"Database verification failed with error: {e}")

if __name__ == "__main__":
    verify_database()
