from typing import Generator
from sqlalchemy.orm import sessionmaker, Session
from backend.config.database import engine

# Create the session factory bound to the engine
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    class_=Session
)

def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency to get a database session.
    Yields the session and ensures it is closed after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
