import uuid
from dataclasses import dataclass, field
from typing import Optional
from uuid import UUID

from .exceptions import DomainError
from .value_objects import Coordinates


@dataclass
class Location:
    id: UUID
    name: str
    coordinates: Coordinates

    @classmethod
    def create(cls, name: str, coordinates: Coordinates, id_: Optional[UUID] = None):
        return cls(id=uuid.uuid4() if not id_ else id_, name=name, coordinates=coordinates)

    def __eq__(self, other):
        if isinstance(other, Location):
            return self.id == other.id
        return False


@dataclass
class User:
    id: UUID
    login: str
    hashed_password: str
    _locations: list[Location] = field(default_factory=list)

    @classmethod
    def create(cls, login: str, hashed_password: str, id_: Optional[UUID] = None):
        return cls(id=uuid.uuid4() if not id_ else id_, login=login, hashed_password=hashed_password)

    def add_location(self, location: Location):
        if location in self._locations:
            raise DomainError("User already has this Location")
        self._locations.append(location)

    def remove_location(self, location: Location):
        if location not in self._locations:
            raise DomainError("Location Not Found")
        self._locations.remove(location)

    @property
    def locations(self):
        return list(self._locations)

    def __eq__(self, other):
        if isinstance(other, User):
            return self.id == other.id
        return False
