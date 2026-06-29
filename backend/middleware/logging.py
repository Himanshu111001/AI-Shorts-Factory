import logging
import os
from logging.handlers import RotatingFileHandler
from backend.config.settings import get_settings

def get_logger(name: str) -> logging.Logger:
    """
    Creates and returns a configured logger with console and rotating file handlers.
    """
    settings = get_settings()
    
    logger = logging.getLogger(name)
    
    # If the logger already has handlers, assume it's already configured
    if logger.handlers:
        return logger

    # Ensure logs directory exists
    log_dir = settings.logs_path
    os.makedirs(log_dir, exist_ok=True)

    # Convert setting string to logging level
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Application Log File Handler (Rotating: 10MB max size, 5 backups)
    app_log_path = os.path.join(log_dir, "application.log")
    app_handler = RotatingFileHandler(
        app_log_path, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
    )
    app_handler.setFormatter(formatter)
    logger.addHandler(app_handler)

    # Error Log File Handler (Rotating: 10MB max size, 5 backups)
    error_log_path = os.path.join(log_dir, "errors.log")
    error_handler = RotatingFileHandler(
        error_log_path, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)

    # Prevent log messages from being propagated to the root logger
    # to avoid duplication.
    logger.propagate = False

    return logger
