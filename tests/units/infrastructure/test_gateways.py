import time
import uuid
from decimal import Decimal

import pytest
from sqlalchemy import select

from weather_tracker.domain.entities import Location, User
from weather_tracker.domain.value_objects import Coordinates
from weather_tracker.infrastructure.database.gateways import PgOrmLocationGateway, PgOrmUserGateway
from weather_tracker.infrastructure.database.orm_models import LocationORM, UserLocationORM, UserORM
from weather_tracker.infrastructure.session_gateway import (
    RedisUserSessionGateway,
    SessionNotFoundError,
)


@pytest.mark.asyncio
async def test_add_user(pg_user_gateway: PgOrmUserGateway):
    user = User.create(login="test", hashed_password="hashed_password")
    await pg_user_gateway.save(user=user)
    await pg_user_gateway.session.commit()

    result = await pg_user_gateway.session.get(UserORM, user.id)
    assert result is not None

    assert result.login == "test"


@pytest.mark.asyncio
async def test_find_user_by_login(pg_user_gateway: PgOrmUserGateway):
    user1 = User.create(login="usr1", hashed_password="hashed_password")
    user2 = User.create(login="usr2", hashed_password="hashed_password")
    await pg_user_gateway.save(user=user1)
    await pg_user_gateway.save(user=user2)
    await pg_user_gateway.session.commit()

    user2_copy = await pg_user_gateway.find_by_login(login="usr2")
    assert user2_copy is not None
    assert user2_copy.id == user2.id


@pytest.mark.asyncio
async def test_find_user_by_login_not_exists(pg_user_gateway: PgOrmUserGateway):
    user1 = User.create(login="usr1", hashed_password="hashed_password")
    await pg_user_gateway.save(user=user1)
    await pg_user_gateway.session.commit()

    user2_copy = await pg_user_gateway.find_by_login(login="usr2")
    assert user2_copy is None


@pytest.mark.asyncio
async def test_find_user_by_id(pg_user_gateway: PgOrmUserGateway):
    user1 = User.create(login="usr1", hashed_password="hashed_password")
    user2 = User.create(login="usr2", hashed_password="hashed_password")
    await pg_user_gateway.save(user=user1)
    await pg_user_gateway.save(user=user2)
    await pg_user_gateway.session.commit()

    user1_copy = await pg_user_gateway.find_by_id(user_id=user1.id)
    assert user1_copy is not None
    assert user1_copy.login == user1.login


@pytest.mark.asyncio
async def test_find_user_by_id_not_exists(pg_user_gateway: PgOrmUserGateway):
    user1 = User.create(login="usr1", hashed_password="hashed_password")
    user2 = User.create(login="usr2", hashed_password="hashed_password")
    await pg_user_gateway.save(user=user1)
    await pg_user_gateway.session.commit()

    user2_copy = await pg_user_gateway.find_by_id(user_id=user2.id)
    assert user2_copy is None


@pytest.mark.asyncio
async def test_add_user_with_locations(pg_user_gateway: PgOrmUserGateway):
    user = User.create(login="test", hashed_password="hashed_password")
    loc1 = Location.create(name="Moscow", coordinates=Coordinates(Decimal(50), Decimal(60)))
    user.add_location(loc1)
    await pg_user_gateway.save(user=user)
    await pg_user_gateway.session.commit()

    result = await pg_user_gateway.session.scalars(select(UserLocationORM).where(UserLocationORM.user_id == user.id))
    assert result is not None
    assert len(list(result)) == 1


@pytest.mark.asyncio
async def test_remove_user_with_locations(pg_user_gateway: PgOrmUserGateway):
    user = User.create(login="test", hashed_password="hashed_password")
    loc1 = Location.create(name="Moscow", coordinates=Coordinates(Decimal(50), Decimal(60)))
    user.add_location(loc1)
    await pg_user_gateway.save(user=user)
    await pg_user_gateway.session.commit()

    result = await pg_user_gateway.session.scalars(select(UserLocationORM).where(UserLocationORM.user_id == user.id))
    assert result is not None
    assert len(list(result)) == 1

    user.remove_location(loc1)
    await pg_user_gateway.save(user=user)
    await pg_user_gateway.session.commit()

    result = await pg_user_gateway.session.scalars(select(UserLocationORM).where(UserLocationORM.user_id == user.id))
    assert len(list(result)) == 0


@pytest.mark.asyncio
async def test_find_user_with_locations(pg_user_gateway: PgOrmUserGateway, pg_location_gateway: PgOrmLocationGateway):
    user = User.create(login="test", hashed_password="hashed_password")
    loc1 = Location.create(name="Moscow", coordinates=Coordinates(Decimal(50), Decimal(60)))
    user.add_location(loc1)
    await pg_location_gateway.save(location=loc1)
    await pg_location_gateway.session.commit()
    await pg_user_gateway.save(user=user)
    await pg_user_gateway.session.commit()

    user_copy = await pg_user_gateway.find_by_id(user_id=user.id, load_locations=True)
    assert user_copy is not None
    assert len(user_copy.locations) == 1
    assert user_copy.locations[0].name == "Moscow"


@pytest.mark.asyncio
async def test_save_location(pg_location_gateway: PgOrmLocationGateway):
    loc = Location.create(name="Moscow", coordinates=Coordinates(Decimal(50), Decimal(60)))
    await pg_location_gateway.save(location=loc)
    await pg_location_gateway.session.commit()

    result = await pg_location_gateway.session.get(LocationORM, loc.id)
    assert result is not None
    assert result.name == "Moscow"


@pytest.mark.asyncio
async def test_get_location_by_coords(pg_location_gateway: PgOrmLocationGateway):
    loc1 = Location.create(name="Moscow", coordinates=Coordinates(Decimal(50), Decimal(60)))
    loc2 = Location.create(name="Kazan", coordinates=Coordinates(Decimal(60), Decimal(60)))
    await pg_location_gateway.save(location=loc1)
    await pg_location_gateway.save(location=loc2)
    await pg_location_gateway.session.commit()

    result = await pg_location_gateway.get_by_coords(coordinates=Coordinates(Decimal(50), Decimal(60)))
    assert result is not None
    assert result.name == "Moscow"


@pytest.mark.asyncio
async def test_get_location_by_coords_not_exists(pg_location_gateway: PgOrmLocationGateway):
    loc1 = Location.create(name="Moscow", coordinates=Coordinates(Decimal(50), Decimal(60)))
    await pg_location_gateway.save(location=loc1)
    await pg_location_gateway.session.commit()

    result = await pg_location_gateway.get_by_coords(coordinates=Coordinates(Decimal(50), Decimal(50)))
    assert result is None


@pytest.mark.asyncio
async def test_create_redis_session(redis_session_gateway: RedisUserSessionGateway):
    user_id = uuid.uuid4()
    session = await redis_session_gateway.create(user_id=user_id)

    result = await redis_session_gateway.redis_client.get(str(session.session_id))
    assert result is not None
    assert user_id == uuid.UUID(result.decode())


@pytest.mark.asyncio
async def test_get_redis_session(redis_session_gateway: RedisUserSessionGateway):
    user_id = uuid.uuid4()
    session = await redis_session_gateway.create(user_id=user_id)

    result = await redis_session_gateway.get_user_id(session_id=session.session_id)
    assert result is not None
    assert user_id == result


@pytest.mark.asyncio
async def test_get_expired_redis_session(redis_session_gateway: RedisUserSessionGateway):
    user_id = uuid.uuid4()
    redis_session_gateway.lifetime = 1
    session = await redis_session_gateway.create(user_id=user_id)
    time.sleep(2)
    with pytest.raises(SessionNotFoundError):
        await redis_session_gateway.get_user_id(session_id=session.session_id)


@pytest.mark.asyncio
async def test_delete_redis_session(redis_session_gateway: RedisUserSessionGateway):
    user_id = uuid.uuid4()
    session = await redis_session_gateway.create(user_id=user_id)
    await redis_session_gateway.delete(session_id=session.session_id)
    with pytest.raises(SessionNotFoundError):
        await redis_session_gateway.get_user_id(session_id=session.session_id)
