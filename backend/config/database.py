from sqlalchemy import create_engine
from backend.config.settings import get_settings

settings = get_settings()

# SQLite requires check_same_thread=False for FastAPI's multi-threaded nature
connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    echo=settings.debug,
)
