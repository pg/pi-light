from datetime import time
from enum import IntEnum
from random import choice, randint
from typing import Optional

from pydantic import BaseModel, Extra, validator

from app.services.pi_light.color import Color
from app.services.pi_light.day import Day
from app.services.simple_time import SimpleTime


class OverlapRegion(IntEnum):
    HEAD = 1
    TAIL = 2


class Rule(BaseModel):
    day: Day = Day.MONDAY
    start_time: time = time(hour=0, minute=0, second=0)
    stop_time: time = time(hour=23, minute=59, second=59)
    start_color: Color = Color()
    stop_color: Color = Color()

    class Config:
        frozen = True
        validate_all = True
        extra = Extra.forbid
        use_enum_values = True

    @validator("stop_time")
    def starttime_after_stoptime(cls, v, values, **kwargs):
        if "start_time" in values and v < values["start_time"]:
            raise ValueError("start_time is after stop_time")
        if "start_time" in values and v == values["start_time"]:
            raise ValueError("start_time equals stop_time")
        return v

    @property
    def hash(self):
        return self.__hash__()

    def within(self, rule) -> bool:
        if self.day != rule.day:
            return False
        return self.start_time >= rule.start_time and self.stop_time <= rule.stop_time

    def overlaps(self, rule, overlap_region: Optional[OverlapRegion] = None) -> bool:
        if self.day != rule.day:
            return False
        if overlap_region == OverlapRegion.HEAD:
            return self.start_time < rule.start_time <= self.stop_time
        elif overlap_region == OverlapRegion.TAIL:
            return self.start_time <= rule.stop_time < self.stop_time
        else:
            return (
                self.within(rule)
                or self.start_time < rule.start_time <= self.stop_time
                or self.start_time <= rule.stop_time < self.stop_time
            )

    def time_interval(self):
        start_str = self.start_time.strftime("%I:%M:%S %p").lstrip("0")
        stop_str = self.stop_time.strftime("%I:%M:%S %p").lstrip("0")
        return f"{start_str} - {stop_str}"

    @staticmethod
    def random():
        start_time = randint(0, 86400)  # nosec
        stop_time = randint(start_time, 86400)  # nosec
        return Rule(
            day=choice(list(Day)),  # nosec
            start_time=SimpleTime.from_seconds(start_time).time(),
            stop_time=SimpleTime.from_seconds(stop_time).time(),
            start_color=Color.random(),  # nosec
            stop_color=Color.random(),  # nosec
        )
