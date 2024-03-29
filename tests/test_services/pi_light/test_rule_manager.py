from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
import time_machine
from pydantic import ValidationError
from testslide import TestCase

from app.services.pi_light.color import Color
from app.services.pi_light.day import Day
from app.services.pi_light.rule import Rule
from app.services.pi_light.rule_manager import RuleDoesNotExistError, RuleManager


class TestRuleManager(TestCase):
    chicago_tz = ZoneInfo("America/Chicago")

    def setUp(self) -> None:
        super().setUp()
        self.rule_manager = RuleManager()

    def test_add_rule_to_day(self) -> None:
        day = Day.MONDAY
        rule = Rule(day=day)

        self.rule_manager.add_rule(rule)

        self.assertListEqual([rule], self.rule_manager.rules[day])

    def test_add_multiple_rules_to_day(self) -> None:
        day = Day.FRIDAY
        rule1 = Rule(day=day, start_time=1, stop_time=3)
        rule2 = Rule(day=day, start_time=5, stop_time=8)

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)

        self.assertListEqual([rule1, rule2], self.rule_manager.rules[day])

    def test_rules_are_sorted(self) -> None:
        day = Day.FRIDAY
        rule1 = Rule(day=day, start_time=1, stop_time=3)
        rule2 = Rule(day=day, start_time=5, stop_time=8)
        rule3 = Rule(day=day, start_time=9, stop_time=11)
        rule4 = Rule(day=day, start_time=14, stop_time=19)

        self.rule_manager.add_rule(rule2)
        self.rule_manager.add_rule(rule4)
        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule3)

        self.assertListEqual([rule1, rule2, rule3, rule4], self.rule_manager.rules[day])

    def test_rules_conflict_inside_existing(self) -> None:
        day = Day.TUESDAY
        rule1 = Rule(day=day, start_time=5, stop_time=19)
        rule2 = Rule(day=day, start_time=8, stop_time=11)

        new_rule1 = Rule(day=day, start_time=5, stop_time=7)
        new_rule2 = Rule(day=day, start_time=12, stop_time=19)

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)

        self.assertListEqual(
            [new_rule1, rule2, new_rule2], self.rule_manager.rules[day]
        )

    def test_rules_conflict_overlap_head(self) -> None:
        day = Day.TUESDAY
        rule1 = Rule(day=day, start_time=5, stop_time=19)
        rule2 = Rule(day=day, start_time=1, stop_time=8)

        new_rule1 = Rule(day=day, start_time=9, stop_time=19)

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)

        self.assertListEqual([rule2, new_rule1], self.rule_manager.rules[day])

    def test_rules_conflict_overlap_tail(self) -> None:
        day = Day.TUESDAY
        rule1 = Rule(day=day, start_time=1, stop_time=8)
        rule2 = Rule(day=day, start_time=5, stop_time=19)

        new_rule1 = Rule(day=day, start_time=1, stop_time=4)

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)

        self.assertListEqual([new_rule1, rule2], self.rule_manager.rules[day])

    def test_rules_conflict_touch_head(self) -> None:
        day = Day.TUESDAY
        rule1 = Rule(day=day, start_time=5, stop_time=19)
        rule2 = Rule(day=day, start_time=1, stop_time=5)

        new_rule1 = Rule(day=day, start_time=6, stop_time=19)

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)

        self.assertListEqual([rule2, new_rule1], self.rule_manager.rules[day])

    def test_rules_conflict_touch_tail(self) -> None:
        day = Day.TUESDAY
        rule1 = Rule(day=day, start_time=1, stop_time=8)
        rule2 = Rule(day=day, start_time=8, stop_time=19)

        new_rule1 = Rule(day=day, start_time=1, stop_time=7)

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)

        self.assertListEqual([new_rule1, rule2], self.rule_manager.rules[day])

    def test_rules_conflict_full_overlap(self) -> None:
        day = Day.TUESDAY
        rule1 = Rule(day=day, start_time=5, stop_time=8)
        rule2 = Rule(day=day, start_time=1, stop_time=19)

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)

        self.assertListEqual([rule2], self.rule_manager.rules[day])

    def test_rules_conflict_overlap_head_tail(self) -> None:
        day = Day.TUESDAY
        rule1 = Rule(day=day, start_time=1, stop_time=8)
        rule2 = Rule(day=day, start_time=10, stop_time=19)
        rule3 = Rule(day=day, start_time=5, stop_time=12)

        new_rule1 = Rule(day=day, start_time=1, stop_time=4)
        new_rule2 = Rule(day=day, start_time=13, stop_time=19)

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)
        self.rule_manager.add_rule(rule3)

        self.assertListEqual(
            [new_rule1, rule3, new_rule2], self.rule_manager.rules[day]
        )

    def test_rules_conflict_overlap_tail_and_whole(self) -> None:
        day = Day.TUESDAY
        rule1 = Rule(day=day, start_time=1, stop_time=8)
        rule2 = Rule(day=day, start_time=10, stop_time=19)
        rule3 = Rule(day=day, start_time=5, stop_time=22)

        new_rule1 = Rule(day=day, start_time=1, stop_time=4)

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)
        self.rule_manager.add_rule(rule3)

        self.assertListEqual([new_rule1, rule3], self.rule_manager.rules[day])

    def test_rules_conflict_overlap_whole_and_head(self) -> None:
        day = Day.TUESDAY
        rule1 = Rule(day=day, start_time=6, stop_time=8)
        rule2 = Rule(day=day, start_time=10, stop_time=19)
        rule3 = Rule(day=day, start_time=3, stop_time=14)

        new_rule1 = Rule(day=day, start_time=15, stop_time=19)

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)
        self.rule_manager.add_rule(rule3)

        self.assertListEqual([rule3, new_rule1], self.rule_manager.rules[day])

    def test_rules_conflict_overlap_tail_whole_head(self) -> None:
        day = Day.TUESDAY
        rule1 = Rule(day=day, start_time=1, stop_time=5)
        rule2 = Rule(day=day, start_time=7, stop_time=9)
        rule3 = Rule(day=day, start_time=11, stop_time=15)
        rule4 = Rule(day=day, start_time=3, stop_time=12)

        new_rule1 = Rule(day=day, start_time=1, stop_time=2)
        new_rule2 = Rule(day=day, start_time=13, stop_time=15)

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)
        self.rule_manager.add_rule(rule3)
        self.rule_manager.add_rule(rule4)

        self.assertListEqual(
            [new_rule1, rule4, new_rule2], self.rule_manager.rules[day]
        )

    def test_rules_conflict_overlap_multiple_whole(self) -> None:
        day = Day.TUESDAY
        rule1 = Rule(day=day, start_time=4, stop_time=8)
        rule2 = Rule(day=day, start_time=10, stop_time=15)
        rule3 = Rule(day=day, start_time=19, stop_time=21)
        rule4 = Rule(day=day, start_time=1, stop_time=42)

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)
        self.rule_manager.add_rule(rule3)
        self.rule_manager.add_rule(rule4)

        self.assertListEqual([rule4], self.rule_manager.rules[day])

    def test_add_conflicting_rules_to_day(self) -> None:
        day = Day.TUESDAY
        rule1 = Rule(day=day, start_time=1, stop_time=19)
        rule2 = Rule(day=day, start_time=5, stop_time=8)
        rule3 = Rule(day=day, start_time=13, stop_time=29)
        rule4 = Rule(day=day, start_time=13, stop_time=29)
        rule5 = Rule(day=day, start_time=40, stop_time=42)
        rule6 = Rule(day=day, start_time=39, stop_time=53)
        rule7 = Rule(day=day, start_time=52, stop_time=65)
        rule8 = Rule(day=day, start_time=49, stop_time=55)
        rule9 = Rule(day=day, start_time=37, stop_time=41)

        new_rule1 = Rule(day=day, start_time=1, stop_time=4)
        new_rule2 = Rule(day=day, start_time=5, stop_time=8)
        new_rule3 = Rule(day=day, start_time=9, stop_time=12)
        new_rule4 = Rule(day=day, start_time=13, stop_time=29)
        new_rule5 = Rule(day=day, start_time=42, stop_time=48)
        new_rule6 = Rule(day=day, start_time=56, stop_time=65)

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)
        self.rule_manager.add_rule(rule3)
        self.rule_manager.add_rule(rule4)
        self.rule_manager.add_rule(rule5)
        self.rule_manager.add_rule(rule6)
        self.rule_manager.add_rule(rule7)
        self.rule_manager.add_rule(rule8)
        self.rule_manager.add_rule(rule9)

        self.assertListEqual(
            [
                new_rule1,
                new_rule2,
                new_rule3,
                new_rule4,
                rule9,
                new_rule5,
                rule8,
                new_rule6,
            ],
            self.rule_manager.rules[day],
        )

    def test_add_invalid_rule_invalid_start_time(self) -> None:
        with pytest.raises(ValidationError):
            self.rule_manager.add_rule(Rule(start_time=30, stop_time=8))

    def test_add_invalid_rule_bad_start_time(self) -> None:
        with pytest.raises(OverflowError):
            self.rule_manager.add_rule(Rule(start_time=-1, stop_time=8))

    def test_add_invalid_rule_bad_stop_time(self) -> None:
        with pytest.raises(OverflowError):
            self.rule_manager.add_rule(Rule(start_time=20, stop_time=-1))

    def test_add_invalid_rule_bad_color(self) -> None:
        with pytest.raises(ValidationError):
            self.rule_manager.add_rule(Rule(start_color=Color(r=-1)))

    def test_remove_rule(self) -> None:
        day = Day(datetime.now().strftime("%A"))
        rule1 = Rule(day=day, start_time="0:0:0", stop_time="0:0:2")
        rule2 = Rule(day=day, start_time="0:0:4", stop_time="0:0:6")

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)
        self.rule_manager.remove_rule(rule1)

        self.assertListEqual([rule2], self.rule_manager.rules[day])

    def test_remove_rule_does_not_exist(self) -> None:
        day = Day(datetime.now().strftime("%A"))
        rule1 = Rule(day=day, start_time="0:0:0", stop_time="0:0:2")
        rule2 = Rule(day=day, start_time="0:0:4", stop_time="0:0:6")
        rule3 = Rule(day=day, start_time="0:0:9", stop_time="0:0:12")

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)

        with pytest.raises(RuleDoesNotExistError):
            self.rule_manager.remove_rule(rule3)

        self.assertListEqual([rule1, rule2], self.rule_manager.rules[day])

    @time_machine.travel(datetime(2021, 4, 27, 0, 0, 5, tzinfo=chicago_tz))
    def test_remove_rule_by_hash(self) -> None:
        day = Day(datetime.now().strftime("%A"))
        rule1 = Rule(day=day, start_time="0:0:0", stop_time="0:0:2")
        rule2 = Rule(day=day, start_time="0:0:4", stop_time="0:0:6")
        rule3 = Rule(day=day, start_time="0:0:9", stop_time="0:0:59")

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)
        self.rule_manager.add_rule(rule3)

        self.rule_manager.remove_rule_by_hash(hash(rule2))

        self.assertNotIn(rule2, self.rule_manager.rules[day])

    @time_machine.travel(datetime(2021, 4, 27, 0, 0, 5, tzinfo=chicago_tz))
    def test_remove_rule_by_hash_rule_not_found(self) -> None:
        day = Day(datetime.now().strftime("%A"))
        rule1 = Rule(day=day, start_time="0:0:0", stop_time="0:0:2")
        rule2 = Rule(day=day, start_time="0:0:4", stop_time="0:0:6")
        rule3 = Rule(day=day, start_time="0:0:9", stop_time="0:0:59")

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)

        with pytest.raises(RuleDoesNotExistError):
            self.rule_manager.remove_rule_by_hash(hash(rule3))

    @time_machine.travel(datetime(2021, 4, 27, 0, 0, 5, tzinfo=chicago_tz))
    def test_current_rule(self) -> None:
        day = Day(datetime.now().strftime("%A"))
        rule1 = Rule(day=day, start_time="0:0:0", stop_time="0:0:2")
        rule2 = Rule(day=day, start_time="0:0:4", stop_time="0:0:6")
        rule3 = Rule(day=day, start_time="0:0:8", stop_time="0:0:20")

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)
        self.rule_manager.add_rule(rule3)

        actual_rule, percentage = self.rule_manager.current_rule()

        self.assertEqual(rule2, actual_rule)
        self.assertAlmostEqual(0.5, percentage, delta=0.01)

    @time_machine.travel(datetime(2021, 4, 27, 12, 0, 5, tzinfo=chicago_tz))
    def test_current_rule_default(self) -> None:
        day = Day(datetime.now().strftime("%A"))
        rule1 = Rule(day=day, start_time="0:0:0", stop_time="0:0:2")
        rule2 = Rule(day=day, start_time="0:0:8", stop_time="0:0:20")

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)

        actual_rule, percentage = self.rule_manager.current_rule()

        self.assertEqual(None, actual_rule)
        self.assertEqual(0.0, percentage)

    @time_machine.travel(datetime(2021, 4, 27, 0, 0, 5, tzinfo=chicago_tz))
    def test_next_rule_in_rule(self) -> None:
        day = Day(datetime.now().strftime("%A"))
        rule1 = Rule(day=day, start_time="0:0:0", stop_time="0:0:2")
        rule2 = Rule(day=day, start_time="0:0:4", stop_time="0:0:5")
        rule3 = Rule(day=day, start_time="0:0:6", stop_time="0:0:20")

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)
        self.rule_manager.add_rule(rule3)

        actual_rule, actual_delta = self.rule_manager.next_rule()

        self.assertEqual(rule3, actual_rule)
        self.assertEqual(1, actual_delta.total_seconds())

    @time_machine.travel(datetime(2021, 4, 27, 0, 0, 8, tzinfo=chicago_tz))
    def test_next_rule_in_last_rule(self) -> None:
        day = Day(datetime.now().strftime("%A"))
        rule1 = Rule(day=day, start_time="0:0:0", stop_time="0:0:2")
        rule2 = Rule(day=day, start_time="0:0:4", stop_time="0:0:5")
        rule3 = Rule(day=day, start_time="0:0:6", stop_time="0:0:20")

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)
        self.rule_manager.add_rule(rule3)

        actual_rule, actual_delta = self.rule_manager.next_rule()

        self.assertEqual(None, actual_rule)
        self.assertEqual(12, actual_delta.total_seconds())

    @time_machine.travel(datetime(2021, 4, 27, 0, 0, 15, tzinfo=chicago_tz))
    def test_next_rule_in_rule_then_gap(self) -> None:
        day = Day(datetime.now().strftime("%A"))
        rule1 = Rule(day=day, start_time="0:0:0", stop_time="0:0:2")
        rule2 = Rule(day=day, start_time="0:0:8", stop_time="0:0:20")
        rule3 = Rule(day=day, start_time="0:0:30", stop_time="0:3:20")

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)
        self.rule_manager.add_rule(rule3)

        actual_rule, actual_delta = self.rule_manager.next_rule()

        self.assertEqual(None, actual_rule)
        self.assertEqual(5, actual_delta.total_seconds())

    @time_machine.travel(datetime(2021, 4, 27, 0, 0, 5, tzinfo=chicago_tz))
    def test_next_rule_not_in_rule(self) -> None:
        day = Day(datetime.now().strftime("%A"))
        rule1 = Rule(day=day, start_time="0:0:0", stop_time="0:0:2")
        rule2 = Rule(day=day, start_time="0:0:8", stop_time="0:0:20")

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)

        actual_rule, actual_delta = self.rule_manager.next_rule()

        self.assertEqual(rule2, actual_rule)
        self.assertEqual(3, actual_delta.total_seconds())

    @time_machine.travel(datetime(2021, 4, 27, 0, 0, 1, tzinfo=chicago_tz))
    def test_next_rule_not_in_rule2(self) -> None:
        day = Day(datetime.now().strftime("%A"))
        rule1 = Rule(day=day, start_time="0:0:3", stop_time="0:0:5")
        rule2 = Rule(day=day, start_time="0:0:8", stop_time="0:0:20")

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)

        actual_rule, actual_delta = self.rule_manager.next_rule()

        self.assertEqual(rule1, actual_rule)
        self.assertEqual(2, actual_delta.total_seconds())

    @time_machine.travel(datetime(2021, 4, 27, 1, 0, 0, tzinfo=chicago_tz))
    def test_next_rule_not_in_rule_none_left(self) -> None:
        day = Day(datetime.now().strftime("%A"))
        rule1 = Rule(day=day, start_time="0:0:3", stop_time="0:0:5")
        rule2 = Rule(day=day, start_time="0:0:8", stop_time="0:0:20")

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)

        actual_rule, actual_delta = self.rule_manager.next_rule()

        self.assertEqual(None, actual_rule)
        self.assertEqual(86400, actual_delta.total_seconds())

    @time_machine.travel(datetime(2021, 4, 27, 0, 0, 5, tzinfo=chicago_tz))
    def test_next_rule_not_in_rule_none(self) -> None:
        actual_rule, actual_delta = self.rule_manager.next_rule()

        self.assertEqual(None, actual_rule)
        self.assertEqual(86400, actual_delta.total_seconds())

    @time_machine.travel(datetime(2021, 4, 27, 1, 2, 3, tzinfo=chicago_tz))
    def test_color(self) -> None:
        day = Day(datetime.now().strftime("%A"))
        color = Color(r=1, g=2, b=4, brightness=0.5)
        rule = Rule(day=day, start_color=color, stop_color=color)

        self.rule_manager.add_rule(rule)

        self.assertEqual(color, self.rule_manager.current_color())

    @time_machine.travel(datetime(2021, 4, 27, 1, 2, 3, tzinfo=chicago_tz))
    def test_color_default(self) -> None:
        self.assertEqual(Color(), self.rule_manager.current_color())

    @time_machine.travel(datetime(2021, 4, 27, 12, 0, 0, tzinfo=chicago_tz))
    def test_color_different_start_stop_color(self) -> None:
        day = Day(datetime.now().strftime("%A"))
        start_color = Color(r=1, g=2, b=4, brightness=0.5)
        stop_color = Color(r=3, g=2, b=8, brightness=1)
        rule = Rule(day=day, start_color=start_color, stop_color=stop_color)
        expected_color = Color(r=2, g=2, b=6, brightness=0.75)

        self.rule_manager.add_rule(rule)

        self.assertEqual(expected_color.r, self.rule_manager.current_color().r)
        self.assertEqual(expected_color.g, self.rule_manager.current_color().g)
        self.assertEqual(expected_color.b, self.rule_manager.current_color().b)
        self.assertAlmostEqual(
            expected_color.brightness, self.rule_manager.current_color().brightness, 4
        )

    @time_machine.travel(datetime(2021, 4, 27, 13, 2, 3, tzinfo=chicago_tz))
    def test_color_multiple_rules(self) -> None:
        day = Day(datetime.now().strftime("%A"))
        color1 = Color(r=1, g=2, b=4, brightness=0.5)
        rule1 = Rule(day=day, stop_time="12:0:0", start_color=color1, stop_color=color1)
        color2 = Color(r=100, g=200, b=150, brightness=1)
        rule2 = Rule(
            day=day, start_time="12:0:1", start_color=color2, stop_color=color2
        )

        self.rule_manager.add_rule(rule1)
        self.rule_manager.add_rule(rule2)

        self.assertEqual(color2, self.rule_manager.current_color())
