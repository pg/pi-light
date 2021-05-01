from pydantic import BaseModel, Field, Extra


class Color(BaseModel):
    r: int = Field(0, ge=0, le=255, title="Red")
    g: int = Field(0, ge=0, le=255, title="Green")
    b: int = Field(0, ge=0, le=255, title="Blue")
    brightness: float = Field(0, ge=0, le=1)

    class Config:
        frozen = True
        validate_all = True
        extra = Extra.forbid

    @property
    def hex(self) -> str:
        return "#{:02x}{:02x}{:02x}".format(self.r, self.g, self.b)

    def __str__(self) -> str:
        return f"({self.r}, {self.g}, {self.b}, {self.brightness})"

    @staticmethod
    def from_hex(hex_str: str, brightness: float = 0.0):
        h = hex_str.lstrip('#')
        rgb = tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
        return Color(r=rgb[0], g=rgb[1], b=rgb[2], brightness=brightness)

    @staticmethod
    def gradient(c1, c2, percentage: float):
        r = c1.r + (c2.r - c1.r) * percentage
        g = c1.g + (c2.g - c1.g) * percentage
        b = c1.b + (c2.b - c1.b) * percentage
        brightness = c1.brightness + (c2.brightness - c1.brightness) * percentage
        return Color(r=r, g=g, b=b, brightness=brightness)
