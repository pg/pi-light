from datetime import datetime, timedelta
from enum import IntEnum
from random import randint
from typing import Optional

from pydantic import BaseModel, Extra, Field, validator

from app.services.pi_light.color import Color


class OverlapRegion(IntEnum):
    HEAD = 1
    TAIL = 2


class Rule(BaseModel):
    start_time: int = Field(0, ge=0, lt=86400000)  # Time is in msec within 24hr day
    stop_time: int = Field(86400000, gt=0, le=86400000)
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

    def within(self, rule) -> bool:
        return self.start_time >= rule.start_time and self.stop_time <= rule.stop_time

    def overlaps(self, rule, overlap_region: Optional[OverlapRegion] = None) -> bool:
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
        d = datetime(2020, 1, 1)
        start_str = (
            (d + timedelta(microseconds=self.start_time * 1000))
            .strftime("%I:%M:%S %p")
            .lstrip("0")
        )
        stop_str = (
            (d + timedelta(microseconds=self.stop_time * 1000))
            .strftime("%I:%M:%S %p")
            .lstrip("0")
        )
        return f"{start_str} - {stop_str}"

    @staticmethod
    def random():
        start_time = randint(0, 86400000)  # nosec
        stop_time = randint(start_time, 86400000)  # nosec
        return Rule(
            start_time=start_time,
            stop_time=stop_time,
            start_color=Color.random(),  # nosec
            stop_color=Color.random(),  # nosec
        )
