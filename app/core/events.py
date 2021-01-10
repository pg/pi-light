from typing import Callable

from fastapi import FastAPI
from loguru import logger

from app.core.config import Settings
from app.core.settings import get_settings


def create_start_app_handler(
    app: FastAPI, settings: Settings = get_settings()
) -> Callable:  # type: ignore
    async def start_app() -> None:
        pass

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:  # type: ignore
    @logger.catch
    async def stop_app() -> None:
        pass

    return stop_app
