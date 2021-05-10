import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from app.core.config import Settings
from app.core.settings import get_settings
from app.services.pi_light.color import Color
from app.services.pi_light.day import Day
from app.services.pi_light.rule import OverlapRegion, Rule

if get_settings().environment == "prod":
    from app.services.pi_light.board import Board
else:
    from app.services.pi_light.fake_board import Board  # type: ignore


class RuleDoesNotExistError(Exception):
    pass


class Light:
    rules: Dict[Day, List[Rule]]
    board: Board

    def __init__(self):
        self.rules = {day: [] for day in Day}
        self.board = Board()

    def add_rule(self, rule: Rule, day: Day) -> None:
        rules = self.rules[day]
        if not rules or rule.start_time > rules[-1].stop_time:
            return rules.append(rule)
        if rule.stop_time < rules[0].start_time:
            return rules.insert(0, rule)

        # Add in sorted order
        new_rules = []
        rule_added = False
        for r in rules:
            # existing rule is within new rule
            if r.within(rule):
                continue
            # new rule is within existing rule
            elif rule.within(r):
                new_head = Rule(
                    start_time=r.start_time,
                    stop_time=rule.start_time - 1,
                    start_color=r.start_color,
                    stop_color=r.stop_color,
                )
                new_rules.append(new_head)
                new_rules.append(rule)
                new_tail = Rule(
                    start_time=rule.stop_time + 1,
                    stop_time=r.stop_time,
                    start_color=r.start_color,
                    stop_color=r.stop_color,
                )
                new_rules.append(new_tail)
                rule_added = True
                continue
            # new rule is before existing rule
            elif not rule_added and rule.stop_time < r.start_time:
                new_rules.append(rule)
                new_rules.append(r)
                rule_added = True
                continue
            # new rule overlaps head of existing rule
            elif rule.overlaps(r, OverlapRegion.HEAD):
                if not rule_added:
                    new_rules.append(rule)
                    rule_added = True
                new_rule = Rule(
                    start_time=rule.stop_time + 1,
                    stop_time=r.stop_time,
                    start_color=r.start_color,
                    stop_color=r.stop_color,
                )
                new_rules.append(new_rule)
                continue
            # new rule overlaps tail of existing rule
            elif rule.overlaps(r, OverlapRegion.TAIL):
                new_rule = Rule(
                    start_time=r.start_time,
                    stop_time=rule.start_time - 1,
                    start_color=r.start_color,
                    stop_color=r.stop_color,
                )
                new_rules.append(new_rule)
                if not rule_added:
                    new_rules.append(rule)
                    rule_added = True
                continue
            new_rules.append(r)
        if not rule_added:
            new_rules.append(rule)
        self.rules[day] = new_rules

    def remove_rule(self, rule: Rule, day: Day) -> None:
        if rule not in self.rules[day]:
            raise RuleDoesNotExistError()
        self.rules[day].remove(rule)

    def remove_rule_by_hash(self, rule_hash: int) -> None:
        for day, rules in self.rules.items():
            hashed_day_rules = list(map(hash, rules))
            try:
                rule_ix = hashed_day_rules.index(rule_hash)
            except ValueError:
                continue
            return self.remove_rule(rules[rule_ix], day)
        raise RuleDoesNotExistError()

    def current_rule(self) -> Tuple[Optional[Rule], float]:
        now = datetime.now()
        day = Day(now.strftime("%A"))
        msec = int(
            (
                now - now.replace(hour=0, minute=0, second=0, microsecond=0)
            ).total_seconds()
            * 1000
        )
        for r in self.rules[day]:
            if r.start_time <= msec <= r.stop_time:
                percentage = (msec - r.start_time) / (r.stop_time - r.start_time)
                return r, percentage

        return None, 0.0

    def next_rule(self) -> Tuple[Optional[Rule], timedelta]:
        now = datetime.now()
        day = Day(now.strftime("%A"))
        msec = int(
            (
                now - now.replace(hour=0, minute=0, second=0, microsecond=0)
            ).total_seconds()
            * 1000
        )
        for index, r in enumerate(self.rules[day]):
            # if before first rule
            if msec < r.start_time:
                return r, timedelta(seconds=round((r.start_time - msec) / 1000.0))
            # if checking last rule
            if index + 1 == len(self.rules[day]):
                if r.start_time <= msec <= r.stop_time:
                    return (
                        None,
                        timedelta(seconds=round((r.stop_time - msec) / 1000.0)),
                    )
                return None, timedelta(days=1)
            next_rule = self.rules[day][index + 1]
            if msec > next_rule.start_time:
                continue
            # if in a rule
            if r.start_time <= msec <= r.stop_time:
                # if next rule is immediate, return it
                if r.stop_time + 1 == next_rule.start_time:
                    return (
                        next_rule,
                        timedelta(seconds=round((r.stop_time - msec) / 1000.0)),
                    )
                # if next rule is not immediate, return None
                else:
                    return (
                        None,
                        timedelta(seconds=round((r.stop_time - msec) / 1000.0)),
                    )
            else:
                return (
                    next_rule,
                    timedelta(seconds=round((next_rule.start_time - msec) / 1000.0)),
                )
        return None, timedelta(days=1)

    def color(self) -> Color:
        current_rule, percentage = self.current_rule()
        if not current_rule:
            return Color()
        return Color.gradient(
            current_rule.start_color, current_rule.stop_color, percentage
        )

    def run(self, settings: Settings = get_settings()) -> None:
        while True:
            self.board.display(self.color())
            time.sleep(settings.sleep_ms / 1000)
