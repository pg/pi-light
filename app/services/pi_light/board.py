from app.core.settings import get_settings
from app.services.pi_light.color import Color

import board
import neopixel


class Board:
    pixels = neopixel.NeoPixel(
        board.D10,
        get_settings().led_count,
        brightness=get_settings().default_brightness
    )

    @classmethod
    def display(cls, color: Color) -> None:
        cls.pixels.brightness = color.brightness
        cls.pixels.fill((color.r, color.g, color.b))