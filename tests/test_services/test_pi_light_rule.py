from unittest import TestCase

from app.services.pi_light.rule import PiLightRule, OverlapRegion


class TestPiLightRule(TestCase):
    def test_within(self) -> None:
        rule1 = PiLightRule(start_time=1, stop_time=8)
        rule2 = PiLightRule(start_time=5, stop_time=8)
        rule3 = PiLightRule(start_time=5, stop_time=8)
        rule4 = PiLightRule(start_time=5, stop_time=9)

        self.assertTrue(rule2.within(rule1))
        self.assertTrue(rule2.within(rule3))
        self.assertTrue(rule3.within(rule2))
        self.assertFalse(rule1.within(rule2))
        self.assertFalse(rule1.within(rule4))
        self.assertFalse(rule4.within(rule1))

    def test_overlaps(self) -> None:
        rule1 = PiLightRule(start_time=3, stop_time=8)
        rule2 = PiLightRule(start_time=5, stop_time=8)
        rule3 = PiLightRule(start_time=5, stop_time=9)
        rule4 = PiLightRule(start_time=1, stop_time=9)
        rule5 = PiLightRule(start_time=1, stop_time=3)

        self.assertTrue(rule1.overlaps(rule2))
        self.assertTrue(rule2.overlaps(rule1))
        self.assertTrue(rule3.overlaps(rule2))
        self.assertTrue(rule2.overlaps(rule3))
        self.assertTrue(rule4.overlaps(rule3))
        self.assertTrue(rule3.overlaps(rule4))
        self.assertFalse(rule3.overlaps(rule5))
        self.assertFalse(rule5.overlaps(rule3))
        self.assertFalse(rule2.overlaps(rule5))

    def test_overlaps_head(self) -> None:
        rule1 = PiLightRule(start_time=1, stop_time=8)
        rule2 = PiLightRule(start_time=5, stop_time=8)
        rule3 = PiLightRule(start_time=5, stop_time=8)
        rule4 = PiLightRule(start_time=5, stop_time=9)
        rule5 = PiLightRule(start_time=7, stop_time=9)

        self.assertTrue(rule1.overlaps(rule2, OverlapRegion.HEAD))
        self.assertFalse(rule2.overlaps(rule1, OverlapRegion.HEAD))
        self.assertFalse(rule2.overlaps(rule3, OverlapRegion.HEAD))
        self.assertFalse(rule3.overlaps(rule2, OverlapRegion.HEAD))
        self.assertFalse(rule2.overlaps(rule4, OverlapRegion.HEAD))
        self.assertTrue(rule2.overlaps(rule5, OverlapRegion.HEAD))
        self.assertFalse(rule5.overlaps(rule2, OverlapRegion.HEAD))

    def test_overlaps_tail(self) -> None:
        rule1 = PiLightRule(start_time=1, stop_time=8)
        rule2 = PiLightRule(start_time=5, stop_time=8)
        rule3 = PiLightRule(start_time=5, stop_time=8)
        rule4 = PiLightRule(start_time=5, stop_time=9)
        rule5 = PiLightRule(start_time=7, stop_time=9)

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
