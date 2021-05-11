from unittest import TestCase

from app.services.pi_light.day import Day
from app.services.pi_light.rule import OverlapRegion, Rule


class TestRule(TestCase):
    def test_within(self) -> None:
        rule1 = Rule(day=Day.FRIDAY, start_time=1, stop_time=8)
        rule2 = Rule(day=Day.FRIDAY, start_time=5, stop_time=8)
        rule3 = Rule(day=Day.FRIDAY, start_time=5, stop_time=8)
        rule4 = Rule(day=Day.FRIDAY, start_time=5, stop_time=9)
        rule5 = Rule(day=Day.SUNDAY, start_time=6, stop_time=8)

        self.assertTrue(rule2.within(rule1))
        self.assertTrue(rule2.within(rule3))
        self.assertTrue(rule3.within(rule2))
        self.assertFalse(rule1.within(rule2))
        self.assertFalse(rule1.within(rule4))
        self.assertFalse(rule4.within(rule1))
        self.assertFalse(rule5.within(rule4))

    def test_overlaps(self) -> None:
        rule1 = Rule(day=Day.FRIDAY, start_time=3, stop_time=8)
        rule2 = Rule(day=Day.FRIDAY, start_time=5, stop_time=8)
        rule3 = Rule(day=Day.FRIDAY, start_time=5, stop_time=9)
        rule4 = Rule(day=Day.FRIDAY, start_time=1, stop_time=9)
        rule5 = Rule(day=Day.FRIDAY, start_time=1, stop_time=3)
        rule6 = Rule(day=Day.SUNDAY, start_time=1, stop_time=5)

        self.assertTrue(rule1.overlaps(rule2))
        self.assertTrue(rule2.overlaps(rule1))
        self.assertTrue(rule3.overlaps(rule2))
        self.assertTrue(rule2.overlaps(rule3))
        self.assertTrue(rule4.overlaps(rule3))
        self.assertTrue(rule3.overlaps(rule4))
        self.assertFalse(rule3.overlaps(rule5))
        self.assertFalse(rule5.overlaps(rule3))
        self.assertFalse(rule2.overlaps(rule5))
        self.assertFalse(rule6.overlaps(rule5))

    def test_overlaps_head(self) -> None:
        rule1 = Rule(day=Day.FRIDAY, start_time=1, stop_time=8)
        rule2 = Rule(day=Day.FRIDAY, start_time=5, stop_time=8)
        rule3 = Rule(day=Day.FRIDAY, start_time=5, stop_time=8)
        rule4 = Rule(day=Day.FRIDAY, start_time=5, stop_time=9)
        rule5 = Rule(day=Day.FRIDAY, start_time=7, stop_time=9)
        rule6 = Rule(day=Day.SUNDAY, start_time=3, stop_time=8)

        self.assertTrue(rule1.overlaps(rule2, OverlapRegion.HEAD))
        self.assertFalse(rule2.overlaps(rule1, OverlapRegion.HEAD))
        self.assertFalse(rule2.overlaps(rule3, OverlapRegion.HEAD))
        self.assertFalse(rule3.overlaps(rule2, OverlapRegion.HEAD))
        self.assertFalse(rule2.overlaps(rule4, OverlapRegion.HEAD))
        self.assertTrue(rule2.overlaps(rule5, OverlapRegion.HEAD))
        self.assertFalse(rule5.overlaps(rule2, OverlapRegion.HEAD))
        self.assertFalse(rule6.overlaps(rule5, OverlapRegion.HEAD))

    def test_overlaps_tail(self) -> None:
        rule1 = Rule(day=Day.FRIDAY, start_time=1, stop_time=8)
        rule2 = Rule(day=Day.FRIDAY, start_time=5, stop_time=8)
        rule3 = Rule(day=Day.FRIDAY, start_time=5, stop_time=8)
        rule4 = Rule(day=Day.FRIDAY, start_time=5, stop_time=9)
        rule5 = Rule(day=Day.FRIDAY, start_time=7, stop_time=9)
        rule6 = Rule(day=Day.SUNDAY, start_time=8, stop_time=11)

        self.assertFalse(rule1.overlaps(rule2, OverlapRegion.TAIL))
        self.assertFalse(rule2.overlaps(rule1, OverlapRegion.TAIL))
        self.assertFalse(rule2.overlaps(rule3, OverlapRegion.TAIL))
        self.assertFalse(rule3.overlaps(rule2, OverlapRegion.TAIL))
        self.assertFalse(rule2.overlaps(rule4, OverlapRegion.TAIL))
        self.assertTrue(rule4.overlaps(rule2, OverlapRegion.TAIL))
        self.assertTrue(rule4.overlaps(rule3, OverlapRegion.TAIL))
        self.assertTrue(rule5.overlaps(rule2, OverlapRegion.TAIL))
        self.assertTrue(rule5.overlaps(rule3, OverlapRegion.TAIL))
        self.assertTrue(rule5.overlaps(rule1, OverlapRegion.TAIL))
        self.assertFalse(rule1.overlaps(rule5, OverlapRegion.TAIL))
        self.assertFalse(rule2.overlaps(rule5, OverlapRegion.TAIL))
        self.assertFalse(rule4.overlaps(rule5, OverlapRegion.TAIL))
        self.assertFalse(rule5.overlaps(rule4, OverlapRegion.TAIL))
        self.assertFalse(rule6.overlaps(rule5, OverlapRegion.TAIL))

    def test_time_interval(self) -> None:
        rule1 = Rule(start_time=0, stop_time=60000)
        rule2 = Rule(start_time=3600000, stop_time=7200000)
        rule3 = Rule(start_time=46800000, stop_time=50400000)

        self.assertEqual("12:00:00 AM - 12:01:00 AM", rule1.time_interval())
        self.assertEqual("1:00:00 AM - 2:00:00 AM", rule2.time_interval())
        self.assertEqual("1:00:00 PM - 2:00:00 PM", rule3.time_interval())

    def test_random(self) -> None:
        for i in range(20):
            Rule.random()
