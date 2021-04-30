from unittest import TestCase

from app.services.pi_light.color import Color


class TestColor(TestCase):
    def test_from_hex(self) -> None:
        expected_color1 = Color(r=35, g=169, b=221, brightness=0.5)
        expected_color2 = Color(r=35, g=169, b=221)

        self.assertEqual(expected_color1, Color.from_hex("#23a9dd", 0.5))
        self.assertEqual(expected_color2, Color.from_hex("#23a9dd"))

    def test_gradient(self) -> None:
        color1 = Color(r=1, g=2, b=4, brightness=0.5)
        color2 = Color(r=5, g=6, b=10, brightness=1)

        expected_color = Color(r=3, g=4, b=7, brightness=0.75)

        self.assertEqual(expected_color, Color.gradient(color1, color2, 0.5))
