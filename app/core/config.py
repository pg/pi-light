import logging
import os
import sys
from typing import List

from loguru import logger
from pydantic import BaseSettings

from app.core.logging import InterceptHandler


class Settings(BaseSettings):
    debug: bool = True
    app_name: str = "Pi Light"
    version = "0.1.0"
    api_prefix: str = "/api"
    allowed_hosts: List[str] = []
    environment: str = "dev"

    class Config:
        env = os.getenv("ENVIRONMENT", "dev")
        env_file = f"dotenv/{env}.env"


# logging configuration
LOGGING_LEVEL = logging.DEBUG if Settings().debug else logging.INFO
logging.basicConfig(
    handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
)
logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])
