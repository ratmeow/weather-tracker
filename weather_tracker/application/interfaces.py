from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from weather_tracker.domain.entities import Location, User
from weather_tracker.domain.value_objects import Coordinates

from .dto import LocationDTO, LocationWeatherDTO, UserSessionDTO


class UserGateway(ABC):
    @abstractmethod
    async def find_by_login(self, login: str) -> Optional[User]:
        pass

    @abstractmethod
    async def find_by_id(self, user_id: UUID, load_locations: bool = False) -> Optional[User]:
        pass

    @abstractmethod
    async def save(self, user: User) -> None:
        pass


class LocationGateway(ABC):
    @abstractmethod
    async def save(self, location: Location) -> None:
        pass

    @abstractmethod
    async def get_by_coords(self, coordinates: Coordinates) -> Optional[Location]:
        pass


class UserSessionGateway(ABC):
    @abstractmethod
    async def create(self, user_id: UUID) -> UserSessionDTO:
        pass

    @abstractmethod
    async def get_user_id(self, session_id: UUID) -> UUID:
        pass

    @abstractmethod
    async def delete(self, session_id: UUID) -> None:
        pass


class Hasher(ABC):
    @abstractmethod
    def hash(self, text: str) -> str:
        pass

    @abstractmethod
    def verify(self, text: str, hashed_text: str) -> bool:
        pass


class DBSession(ABC):
    @abstractmethod
    async def commit(self) -> None:
        pass


class WeatherClient(ABC):
    @abstractmethod
    async def search_location(self, name: str) -> list[LocationDTO]:
        pass

    @abstractmethod
    async def get_weather_by_location(self, location: Location) -> LocationWeatherDTO:
        pass
