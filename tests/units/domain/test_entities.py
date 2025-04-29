from decimal import Decimal

import pytest

from weather_tracker.domain.entities import Location, User
from weather_tracker.domain.exceptions import DomainError
from weather_tracker.domain.value_objects import Coordinates


def test_user_create():
    user = User.create(login="test", hashed_password="hashed_password")

    assert user.login == "test"
    assert user.hashed_password == "hashed_password"


def test_location_create():
    coordinates = Coordinates(longitude=Decimal(5.0), latitude=Decimal(5))
    location = Location.create(name="Moscow", coordinates=coordinates)
    assert location.name == "Moscow"
    assert location.coordinates.longitude == Decimal(5.0)


def test_user_add_location():
    user = User.create(login="test", hashed_password="hashed_password")
    coordinates = Coordinates(longitude=Decimal(5.0), latitude=Decimal(5))
    moscow = Location.create(name="Moscow", coordinates=coordinates)
    user.add_location(location=moscow)
    assert moscow in user.locations


def test_user_add_same_location():
    user = User.create(login="test", hashed_password="hashed_password")
    coordinates = Coordinates(longitude=Decimal(5.0), latitude=Decimal(5))
    moscow = Location.create(name="Moscow", coordinates=coordinates)
    user.add_location(location=moscow)
    with pytest.raises(DomainError):
        user.add_location(location=moscow)


def test_user_delete_location():
    user = User.create(login="test", hashed_password="hashed_password")
    coordinates = Coordinates(longitude=Decimal(5.0), latitude=Decimal(5))
    moscow = Location.create(name="Moscow", coordinates=coordinates)
    user.add_location(location=moscow)
    user.remove_location(location=moscow)
    assert len(user.locations) == 0


def test_user_delete_nonexistent_location():
    user = User.create(login="test", hashed_password="hashed_password")
    coordinates = Coordinates(longitude=Decimal(5.0), latitude=Decimal(5))
    moscow = Location.create(name="Moscow", coordinates=coordinates)
    user.add_location(location=moscow)

    ufa = Location.create(name="Ufa", coordinates=Coordinates(longitude=Decimal(2), latitude=Decimal(5)))

    with pytest.raises(DomainError):
        user.remove_location(location=ufa)
