from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from backend.config.environment import Environment

class Settings(BaseSettings):
    """
    Application settings.
    Uses pydantic_settings to load from .env file or environment variables.
    """
    app_name: str = "AI Media Factory"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    database_url: str = "sqlite:///./aimf.db"
    storage_path: str = "./storage"
    logs_path: str = "./logs"
    environment: Environment = Environment.DEVELOPMENT

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

@lru_cache
def get_settings() -> Settings:
    """
    Get the singleton instance of Settings.
    """
    return Settings()
