from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class OpenWeatherLocationSearchRequest(BaseModel):
    q: str
    appid: str
    limit: int = 5


class OpenWeatherLocationWeatherRequest(BaseModel):
    lat: Decimal
    lon: Decimal
    units: str = "metric"
    appid: str
