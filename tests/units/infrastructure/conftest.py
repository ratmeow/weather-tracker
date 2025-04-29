from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fakeredis.aioredis import FakeRedis
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from weather_tracker.config import Config
from weather_tracker.infrastructure.database.gateways import PgOrmLocationGateway, PgOrmUserGateway
from weather_tracker.infrastructure.database.orm_models import Base
from weather_tracker.infrastructure.external_api.open_weather_client import OpenWeatherClient
from weather_tracker.infrastructure.session_gateway import RedisUserSessionGateway

from .mocks import MockAsyncHTTPClient, MockDatabase


@pytest.fixture(scope="session")
def async_http_client():
    return MockAsyncHTTPClient(timeout=60)


@pytest.fixture(scope="session")
def test_config():
    return Config.from_env("test.env")


@pytest.fixture(scope="session")
def open_weather_client(async_http_client, test_config):
    return OpenWeatherClient(async_http_client=async_http_client, config=test_config.open_weather)


@pytest_asyncio.fixture
async def database() -> AsyncGenerator[MockDatabase, None]:
    db = MockDatabase(db_url="sqlite+aiosqlite:///:memory:")
    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield db

    async with db.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await db.engine.dispose()


@pytest_asyncio.fixture
async def db_session(database: MockDatabase) -> AsyncGenerator[AsyncSession, None]:
    async with database.async_session_maker() as session:
        yield session


@pytest_asyncio.fixture
async def pg_user_gateway(db_session: AsyncSession) -> PgOrmUserGateway:
    return PgOrmUserGateway(session=db_session)


@pytest_asyncio.fixture
async def pg_location_gateway(db_session: AsyncSession) -> PgOrmLocationGateway:
    return PgOrmLocationGateway(session=db_session)


@pytest.fixture
def redis_client() -> Redis:
    return FakeRedis()


@pytest_asyncio.fixture
async def redis_session_gateway(redis_client, test_config) -> RedisUserSessionGateway:
    return RedisUserSessionGateway(redis_client=redis_client, config=test_config.redis)
