import board
import neopixel

from app.core.settings import get_settings
from app.services.pi_light.color import Color


class Board:
    pixels = neopixel.NeoPixel(
        board.D21,
        get_settings().led_count,
        brightness=get_settings().default_brightness,
    )
    rainbow_step_num = 0

    @classmethod
    def fill(cls, color: Color) -> None:
        cls.pixels.brightness = color.brightness
        cls.pixels.fill((color.r, color.g, color.b))

    @classmethod
    def rainbow_step(cls) -> None:
        for i in range(cls.pixels.n):
            pixel_index = (i * 256 // cls.pixels.n) + cls.rainbow_step_num
            cls.pixels[i] = cls._wheel(pixel_index & 255)
        cls.pixels.show()
        cls.rainbow_step_num += 1
        if cls.rainbow_step_num == 255:
            cls.rainbow_step_num = 0

    @staticmethod
    def _wheel(pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return r, g, b
