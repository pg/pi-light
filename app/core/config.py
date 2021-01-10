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
    environment: str = "test"

    class Config:
        env = os.getenv("ENVIRONMENT", "test")
        env_file = f"dotenv/{env}.env"

    def test_environment(self) -> bool:
        return self.environment == "test" or self.environment == "build-test"


# logging configuration
LOGGING_LEVEL = logging.DEBUG if Settings().debug else logging.INFO
logging.basicConfig(
    handlers=[InterceptHandler(level=LOGGING_LEVEL)], level=LOGGING_LEVEL
)
logger.configure(handlers=[{"sink": sys.stderr, "level": LOGGING_LEVEL}])
