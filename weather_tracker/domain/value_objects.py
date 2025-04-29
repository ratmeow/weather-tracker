from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Coordinates:
    latitude: Decimal
    longitude: Decimal

    def __eq__(self, other):
        if isinstance(other, Coordinates):
            return self.latitude == other.latitude and self.longitude == self.longitude
        return False


@dataclass(frozen=True)
class Weather:
    main_state: str
    temperature: int
    temperature_feels: int
    wind_speed: int
    humidity: int
