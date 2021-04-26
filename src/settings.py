from config import BASE_DIR
from pydantic import BaseModel
from typing import List
import os

file = open(os.path.join(BASE_DIR, 'settings.json'))


class Clip(BaseModel):
    duration_min: int
    duration_max: int
    size_max: int
    extensions: List[str]


class Advertise(BaseModel):
    clip: Clip


class Settings(BaseModel):
    advertise: Advertise


settings = Settings.parse_raw(file.read())
