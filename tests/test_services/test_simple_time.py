from datetime import time
from unittest import TestCase

from app.services.simple_time import SimpleTime


class TestSimpleTime(TestCase):
    def test_simple_time(self):
        self.assertEqual(600, SimpleTime(0, 10, 0).total_seconds())
        self.assertEqual(5400, SimpleTime(1, 30, 0).total_seconds())

    def test_str(self):
        self.assertEqual("00:10:00", str(SimpleTime(0, 10, 0)))
        self.assertEqual("10:10:00", str(SimpleTime(10, 10, 0)))

    def test_add(self):
        self.assertEqual(SimpleTime(0, 10, 0), SimpleTime(0, 0, 0) + 600)
        self.assertEqual(SimpleTime(1, 40, 0), SimpleTime(0, 10, 0) + 5400)

    def test_sub(self):
        self.assertEqual(SimpleTime(0, 0, 0), SimpleTime(0, 10, 0) - 600)
        self.assertEqual(SimpleTime(0, 10, 0), SimpleTime(1, 40, 0) - 5400)

    def test_from_time(self):
        self.assertEqual(SimpleTime(0, 10, 0), SimpleTime.from_time(time(0, 10, 0)))
        self.assertEqual(SimpleTime(1, 30, 0), SimpleTime.from_time(time(1, 30, 0)))

    def test_from_seconds(self):
        self.assertEqual(SimpleTime(0, 10, 0), SimpleTime.from_seconds(600))
        self.assertEqual(SimpleTime(1, 30, 0), SimpleTime.from_seconds(5400))

    def test_time(self):
        self.assertEqual(time(0, 10, 0), SimpleTime(0, 10, 0).time())
        self.assertEqual(time(1, 30, 0), SimpleTime(1, 30, 0).time())

    def test_total_seconds(self):
        self.assertEqual(600, SimpleTime(0, 10, 0).total_seconds())
        self.assertEqual(5400, SimpleTime(1, 30, 0).total_seconds())
