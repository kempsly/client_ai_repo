from loguru import logger
from app.config import Config

logger.add(
    Config.LOG_FILE,
    level=Config.LOG_LEVEL,
    rotation="10 MB",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}"
)
