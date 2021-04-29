import time
from copy import deepcopy
from datetime import datetime
from typing import Tuple

from app.core.config import Settings
from app.core.settings import get_settings
from app.services.pi_light.color import Color
from app.services.pi_light.days import Day
from app.services.pi_light.rule import Rule, OverlapRegion

if get_settings().environment == "prod":
    from app.services.pi_light.board import Board
else:
    from app.services.pi_light.fake_board import Board  # type: ignore


class Light:
    rules: dict[int, list[Rule]]
    board: Board

    def __init__(self):
        self.rules = {i: [] for i in range(7)}

    def add_rule(self, rule: Rule, day: Day) -> None:
        rules = self.rules[day.value]
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
                new_head = deepcopy(r)
                new_head.stop_time = rule.start_time - 1
                new_rules.append(new_head)
                new_rules.append(rule)
                new_tail = deepcopy(r)
                new_tail.start_time = rule.stop_time + 1
                new_rules.append(new_tail)
                rule_added = True
                continue
            # rule is before existing rule
            elif not rule_added and rule.stop_time < r.start_time:
                new_rules.append(rule)
                new_rules.append(r)
                rule_added = True
                continue
            # rule overlaps head of existing rule
            elif rule.overlaps(r, OverlapRegion.HEAD):
                if not rule_added:
                    new_rules.append(rule)
                    rule_added = True
                r.start_time = rule.stop_time + 1
                new_rules.append(r)
                continue
            # rule overlaps tail of existing rule
            elif rule.overlaps(r, OverlapRegion.TAIL):
                r.stop_time = rule.start_time - 1
                new_rules.append(r)
                if not rule_added:
                    new_rules.append(rule)
                    rule_added = True
                continue
            new_rules.append(r)
        if not rule_added:
            new_rules.append(rule)
        self.rules[day.value] = new_rules

    def remove_rule(self, rule: Rule, day: Day) -> None:
        # TODO: add tests and implement
        pass

    def current_rule(self) -> Tuple[Rule, float]:
        now = datetime.now()
        day = now.weekday()
        msec = int((now - now.replace(hour=0, minute=0, second=0,
                                      microsecond=0)).total_seconds() * 1000)
        for r in self.rules[day]:
            if r.start_time <= msec <= r.stop_time:
                percentage = (msec - r.start_time) / (r.stop_time - r.start_time)
                return r, percentage

        return Rule(), 0.0

    def color(self) -> Color:
        current_rule, percentage = self.current_rule()
        return Color.gradient(
            current_rule.start_color, current_rule.stop_color, percentage
        )

    def run(self, settings: Settings = get_settings()) -> None:
        while True:
            self.board.display(self.color())
            time.sleep(settings.sleep_ms / 1000)
