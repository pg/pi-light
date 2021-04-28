from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, Field, validator

from app.services.pi_light.color import PiLightColor


class OverlapRegion(IntEnum):
    HEAD = 1
    TAIL = 2


class PiLightRule(BaseModel):
    # Time is in msec within 24hr day
    start_time: int = Field(0, ge=0, lt=86400000)
    stop_time: int = Field(86400000, gt=0, le=86400000)
    start_color: PiLightColor = PiLightColor()
    stop_color: PiLightColor = PiLightColor()

    @validator('stop_time')
    def starttime_after_stoptime(cls, v, values, **kwargs):
        if 'start_time' in values and v < values['start_time']:
            raise ValueError('start_time is after stop_time')
        if 'start_time' in values and v == values['start_time']:
            raise ValueError('start_time equals stop_time')
        return v

    def within(self, rule) -> bool:
        return self.start_time >= rule.start_time and self.stop_time <= rule.stop_time

    def overlaps(self, rule, overlap_region: Optional[OverlapRegion] = None) -> bool:
        if overlap_region == OverlapRegion.HEAD:
            return self.start_time < rule.start_time < self.stop_time
        elif overlap_region == OverlapRegion.TAIL:
            return self.start_time < rule.stop_time < self.stop_time
        else:
            return (self.within(rule)
                    or self.start_time < rule.start_time < self.stop_time
                    or self.start_time < rule.stop_time < self.stop_time)
