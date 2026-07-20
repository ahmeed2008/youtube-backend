import logging
import sys
from app.core.config import get_settings


def setup_logger(name: str) -> logging.Logger:
    settings = get_settings()
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
    
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(settings.LOG_FORMAT))
        logger.addHandler(handler)
    
    return logger


logger = setup_logger("youtube_service")
