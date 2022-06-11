from datetime import time

import pydantic
from pydantic import Field


@pydantic.dataclasses.dataclass
class SimpleTime:
    """
    A simpler Time class with easy conversion to and from datetime.time,
    and with a few helper methods for arithmetic.
    """

    hour: int = Field(0, ge=0, lt=24)
    minute: int = Field(0, ge=0, lt=60)
    second: int = Field(0, ge=0, lt=60)

    def __str__(self) -> str:
        return f"{self.hour:02}:{self.minute:02}:{self.second:02}"

    def __add__(self, other: int) -> "SimpleTime":
        return self.from_seconds(self.total_seconds() + other)

    def __sub__(self, other: int) -> "SimpleTime":
        return self.from_seconds(self.total_seconds() - other)

    @classmethod
    def from_time(cls, t: time) -> "SimpleTime":
        return cls(hour=t.hour, minute=t.minute, second=t.second)  # type: ignore

    @classmethod
    def from_seconds(cls, seconds: int = Field(0, ge=0, lt=86400)) -> "SimpleTime":
        seconds = seconds % (24 * 3600)
        hours = seconds // 3600
        seconds %= 3600
        minutes = seconds // 60
        seconds %= 60
        return cls(hours, minutes, seconds)  # type: ignore

    def time(self) -> time:
        return time(self.hour, self.minute, self.second)

    def total_seconds(self) -> int:
        return self.hour * 3600 + self.minute * 60 + self.second
