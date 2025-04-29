from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional
from uuid import UUID

from weather_tracker.domain.value_objects import Coordinates


@dataclass
class RegisterUserInput:
    login: str
    password: str


@dataclass
class RegisterUserOutput:
    login: str
    hashed_password: str


@dataclass
class LoginUserInput:
    login: str
    password: str


@dataclass
class LocationDTO:
    name: str
    coordinates: Coordinates
    country: Optional[str] = None
    state: Optional[str] = None

    def to_dict(self):
        return {
            "name": self.name,
            "longitude": self.coordinates.longitude,
            "latitude": self.coordinates.latitude,
            "country": self.country,
            "state": self.state,
        }


@dataclass
class UserSessionDTO:
    session_id: UUID
    user_id: UUID
    expired_ts: datetime


@dataclass
class LocationAddInput:
    name: str
    coordinates: Coordinates


@dataclass
class LocationWeatherDTO:
    name: str
    coordinates: Coordinates
    country: Optional[str]
    main_state: Optional[str]
    temperature: Optional[float | int] = None
    temperature_feels: Optional[float | int] = None
    wind_speed: Optional[float | int] = None
    humidity: Optional[float | int] = None

    def to_dict(self):
        return {
            "name": self.name,
            "longitude": self.coordinates.longitude,
            "latitude": self.coordinates.latitude,
            "country": self.country,
            "main_state": self.main_state,
            "temperature": self.temperature,
            "temperature_feels": self.temperature_feels,
            "wind_speed": self.wind_speed,
            "humidity": self.humidity,
        }
