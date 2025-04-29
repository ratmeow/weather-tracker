from typing import AsyncIterable

import pytest
import pytest_asyncio
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from dishka.integrations.fastapi import setup_dishka
from fakeredis.aioredis import FakeRedis
from fastapi.testclient import TestClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from weather_tracker.app import create_app
from weather_tracker.config import Config
from weather_tracker.infrastructure.database.orm_models import Base
from weather_tracker.ioc import AppProvider


@pytest.fixture(scope="session")
def config():
    return Config.from_env()


class TestProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_redis(self) -> AsyncIterable[Redis]:
        redis = FakeRedis()
        try:
            yield redis
        finally:
            await redis.aclose()

    @provide(scope=Scope.APP)
    async def get_session_maker(self) -> AsyncIterable[async_sessionmaker[AsyncSession]]:
        engine = create_async_engine(url="sqlite+aiosqlite:///:memory:")
        session_maker = async_sessionmaker(engine)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield session_maker

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest_asyncio.fixture(scope="session")
async def ioc(config) -> AsyncContainer:
    container = make_async_container(AppProvider(), TestProvider(), context={Config: config})
    yield container
    await container.close()


@pytest.fixture(scope="session")
def client(ioc):
    app = create_app()
    setup_dishka(ioc, app)
    with TestClient(app=app) as client:
        yield client
