import random
import uuid
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from typing import Optional
from uuid import UUID

from weather_tracker.application.dto import LocationDTO, LocationWeatherDTO, UserSessionDTO
from weather_tracker.application.interfaces import (
    DBSession,
    Hasher,
    LocationGateway,
    UserGateway,
    UserSessionGateway,
    WeatherClient,
)
from weather_tracker.domain.entities import Location, User
from weather_tracker.domain.value_objects import Coordinates


class MockUserGateway(UserGateway):
    def __init__(self):
        self.storage: list[User] = []
        self.user_location_storage: dict[UUID, list[Location]] = {}

    async def find_by_login(self, login: str) -> Optional[User]:
        for usr in self.storage:
            if usr.login == login:
                return usr
        return None

    async def find_by_id(self, user_id: UUID, load_locations: bool = False) -> Optional[User]:
        for usr in self.storage:
            if usr.id == user_id:
                return usr
        return None

    async def save(self, user: User) -> None:
        if user not in self.storage:
            self.storage.append(user)

        self.user_location_storage[user.id] = user.locations


class MockHasher(Hasher):
    def hash(self, text: str) -> str:
        return text

    def verify(self, text: str, hashed_text: str) -> bool:
        return text == hashed_text


class MockUserSessionGateway(UserSessionGateway):
    def __init__(self):
        self.storage: list[UserSessionDTO] = []

    async def create(self, user_id: UUID) -> UserSessionDTO:
        session = UserSessionDTO(
            session_id=uuid.uuid4(), user_id=user_id, expired_ts=datetime.now(tz=UTC) + timedelta(hours=24)
        )
        self.storage.append(session)
        return session

    async def get_user_id(self, session_id: UUID) -> UUID:
        for session in self.storage:
            if session.session_id == session_id:
                return session.user_id
        raise ValueError(f"Session {session_id} not found")

    async def delete(self, session_id: UUID) -> None:
        for session in self.storage:
            if session.session_id == session_id:
                target_session = session
                self.storage.remove(target_session)


class MockDBSession(DBSession):
    async def commit(self) -> None:
        pass


class MockLocationGateway(LocationGateway):
    def __init__(self):
        self.storage: list[Location] = []

    async def save(self, location: Location):
        self.storage.append(location)

    async def get_by_coords(self, coordinates: Coordinates) -> Optional[Location]:
        for loc in self.storage:
            if loc.coordinates == coordinates:
                return loc
        return None


class MockWeatherClient(WeatherClient):
    async def search_location(self, name: str) -> list[LocationDTO]:
        locations = []
        if name not in ["Stalingrad", "Sverdlovsk", "Kuibyshev", "Leningrad"]:
            for i in range(random.randint(1, 5)):
                coords = Coordinates(latitude=Decimal(random.random() * 100), longitude=Decimal(random.random() * 100))
                locations.append(LocationDTO(name=name, coordinates=coords))
        return locations

    async def get_weather_by_location(self, location: Location) -> LocationWeatherDTO:
        return LocationWeatherDTO(
            name=location.name,
            coordinates=location.coordinates,
            country=None,
            temperature=random.randint(-50, 50),
            main_state=None,
            temperature_feels=None,
            humidity=90,
            wind_speed=0,
        )
