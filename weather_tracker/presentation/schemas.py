from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class UserRegisterRequest(BaseModel):
    login: str
    password: str


class UserLoginRequest(BaseModel):
    login: str
    password: str


class LocationResponse(BaseModel):
    name: str
    latitude: Decimal
    longitude: Decimal
    country: Optional[str] = None
    state: Optional[str] = None


class WeatherResponse(LocationResponse):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    temperature: Optional[int] = Field(default=None)
    main_state: Optional[str] = Field(default=None, alias="mainState")
    wind_speed: Optional[int] = Field(default=None, alias="windSpeed")
    temperature_feels: Optional[int] = Field(default=None, alias="temperatureFeels")
    humidity: Optional[int] = Field(default=None)

    @field_validator("temperature", "wind_speed", "temperature_feels", "humidity", mode="before")
    def validate_temp(cls, v):
        try:
            return int(float(v)) if v is not None else None
        except (ValueError, TypeError):
            return None


class LocationRequest(BaseModel):
    name: str
    latitude: Decimal
    longitude: Decimal
