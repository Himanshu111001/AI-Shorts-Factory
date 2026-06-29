from backend.middleware.logging import get_logger

logger = get_logger(__name__)

def init_db() -> None:
    """
    Initializes the database connection and prepares for startup integration.
    Does not create tables yet.
    """
    logger.info("Initializing database...")
    # Future integration: Base.metadata.create_all(bind=engine)
    logger.info("Database initialization prepared successfully.")
