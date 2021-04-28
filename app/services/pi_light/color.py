from pydantic import BaseModel, Field


class PiLightColor(BaseModel):
    r: int = Field(255, ge=0, le=255)
    g: int = Field(255, ge=0, le=255)
    b: int = Field(255, ge=0, le=255)
    brightness: float = Field(1, ge=0, le=1)

    @staticmethod
    def gradient(c1, c2, percentage: float):
        r = c1.r + (c2.r - c1.r) * percentage
        g = c1.g + (c2.g - c1.g) * percentage
        b = c1.b + (c2.b - c1.b) * percentage
        brightness = c1.brightness + (c2.brightness - c1.brightness) * percentage
        return PiLightColor(r=r, g=g, b=b, brightness=brightness)
