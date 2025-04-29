import uuid
from decimal import Decimal

import pytest

from weather_tracker.application.dto import LocationAddInput, LoginUserInput
from weather_tracker.application.exceptions import UserLocationError
from weather_tracker.domain.entities import Location, User
from weather_tracker.domain.value_objects import Coordinates


@pytest.mark.asyncio
async def test_add_new_location(login_user, add_user_location):
    exists_user = User(id=uuid.uuid4(), login="test", hashed_password="hashed_password")
    await add_user_location.user_gateway.save(user=exists_user)

    loc_data = LocationAddInput(name="Moscow", coordinates=Coordinates(latitude=Decimal(50), longitude=Decimal(60)))
    session = await login_user.execute(LoginUserInput(login=exists_user.login, password=exists_user.hashed_password))
    await add_user_location.execute(session_id=str(session.session_id), location_data=loc_data)
    assert len(exists_user.locations) == 1
    assert exists_user.locations[0].name == "Moscow"


@pytest.mark.asyncio
async def test_add_exists_location(add_user_location, login_user):
    exists_user = User(id=uuid.uuid4(), login="test", hashed_password="hashed_password")

    await add_user_location.user_gateway.save(user=exists_user)
    loc_data = LocationAddInput(name="Moscow", coordinates=Coordinates(latitude=Decimal(50), longitude=Decimal(60)))
    exists_location = Location(id=uuid.uuid4(), name=loc_data.name, coordinates=loc_data.coordinates)

    await add_user_location.location_gateway.save(exists_location)
    session = await login_user.execute(LoginUserInput(login=exists_user.login, password=exists_user.hashed_password))

    await add_user_location.execute(session_id=str(session.session_id), location_data=loc_data)

    assert exists_location in exists_user.locations


@pytest.mark.asyncio
async def test_add_exists_location_for_user(add_user_location, login_user):
    loc_data = LocationAddInput(name="Moscow", coordinates=Coordinates(latitude=Decimal(50), longitude=Decimal(60)))
    exists_location = Location(id=uuid.uuid4(), name=loc_data.name, coordinates=loc_data.coordinates)

    await add_user_location.location_gateway.save(exists_location)
    exists_user = User(id=uuid.uuid4(), login="usr", hashed_password="hashed_password")

    exists_user.add_location(location=exists_location)
    await add_user_location.user_gateway.save(user=exists_user)
    session = await login_user.execute(LoginUserInput(login=exists_user.login, password=exists_user.hashed_password))

    with pytest.raises(UserLocationError):
        await add_user_location.execute(session_id=str(session.session_id), location_data=loc_data)


@pytest.mark.asyncio
async def test_remove_location(remove_user_location, login_user):
    loc_data = LocationAddInput(name="Moscow", coordinates=Coordinates(latitude=Decimal(50), longitude=Decimal(60)))
    location = Location(id=uuid.uuid4(), name=loc_data.name, coordinates=loc_data.coordinates)

    await remove_user_location.location_gateway.save(location=location)

    exists_user = User(id=uuid.uuid4(), login="usr", hashed_password="hashed_password")

    exists_user.add_location(location=location)
    await remove_user_location.user_gateway.save(user=exists_user)
    session = await login_user.execute(LoginUserInput(login=exists_user.login, password=exists_user.hashed_password))

    await remove_user_location.execute(session_id=str(session.session_id), location_data=loc_data)

    assert location not in exists_user.locations


@pytest.mark.asyncio
async def test_remove_not_user_location(remove_user_location, login_user):
    loc_data = LocationAddInput(name="Moscow", coordinates=Coordinates(latitude=Decimal(50), longitude=Decimal(60)))
    location = Location(id=uuid.uuid4(), name=loc_data.name, coordinates=loc_data.coordinates)
    await remove_user_location.location_gateway.save(location=location)

    exists_user = User(id=uuid.uuid4(), login="usr", hashed_password="hashed_password")
    await remove_user_location.user_gateway.save(user=exists_user)
    session = await login_user.execute(LoginUserInput(login=exists_user.login, password=exists_user.hashed_password))

    with pytest.raises(UserLocationError):
        await remove_user_location.execute(session_id=str(session.session_id), location_data=loc_data)


@pytest.mark.asyncio
async def test_get_user_locations(get_user_locations, login_user):
    exists_user = User(id=uuid.uuid4(), login="usr", hashed_password="hashed_password")

    location1 = Location(
        id=uuid.uuid4(), name="Moscow", coordinates=Coordinates(latitude=Decimal(50), longitude=Decimal(60))
    )
    location2 = Location(
        id=uuid.uuid4(), name="Kazan", coordinates=Coordinates(latitude=Decimal(60), longitude=Decimal(60))
    )

    await get_user_locations.location_gateway.save(location=location1)
    await get_user_locations.location_gateway.save(location=location2)

    exists_user.add_location(location=location1)
    exists_user.add_location(location=location2)

    await get_user_locations.user_gateway.save(user=exists_user)
    session = await login_user.execute(LoginUserInput(login=exists_user.login, password=exists_user.hashed_password))
    result = await get_user_locations.execute(session_id=str(session.session_id))

    assert len(result) == 2
    assert result[0].name == "Moscow"
    assert result[0].temperature is not None


@pytest.mark.asyncio
async def test_get_user_not_locations(get_user_locations, login_user):
    exists_user = User(id=uuid.uuid4(), login="usr", hashed_password="hashed_password")
    await get_user_locations.user_gateway.save(user=exists_user)
    session = await login_user.execute(LoginUserInput(login=exists_user.login, password=exists_user.hashed_password))
    result = await get_user_locations.execute(session_id=str(session.session_id))

    assert len(result) == 0


@pytest.mark.asyncio
async def test_search_location(search_location):
    result = await search_location.execute(location_name="Moscow")
    assert len(result) >= 1


@pytest.mark.asyncio
async def test_search_not_exists_location(search_location):
    result = await search_location.execute(location_name="Stalingrad")
    assert len(result) == 0
