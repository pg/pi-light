from functools import lru_cache

from app.services.pi_light.light import Light


@lru_cache()
def get_light() -> Light:
    return Light()
