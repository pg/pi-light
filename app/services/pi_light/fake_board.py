from loguru import logger

from app.services.pi_light.color import Color


class Board:
    @classmethod
    def display(cls, color: Color) -> None:
        logger.debug(f"Current Board Color: {color}")
