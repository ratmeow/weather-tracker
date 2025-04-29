import pytest
from dishka import AsyncContainer
from fastapi.testclient import TestClient
from redis.asyncio import Redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from weather_tracker.infrastructure.database.orm_models import LocationORM, UserLocationORM, UserORM


@pytest.mark.asyncio
async def test_register_success(client: TestClient, ioc: AsyncContainer):
    data = {"login": "bob", "password": "password_1"}
    response = client.post("/register", json=data)

    assert response.status_code == 200
    session_maker: async_sessionmaker[AsyncSession] = await ioc.get(async_sessionmaker[AsyncSession])
    async with session_maker() as session:
        result = await session.scalars(select(UserORM).filter_by(login="bob"))
        assert result is not None


@pytest.mark.asyncio
async def test_register_login_failed(client: TestClient):
    data = {"login": "боб", "password": "password_1"}
    response = client.post("/register", json=data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_password_failed(client: TestClient):
    data = {"login": "bob", "password": "password"}
    response = client.post("/register", json=data)

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_user_already_exists(client: TestClient):
    data = {"login": "bob", "password": "password_1"}
    response = client.post("/register", json=data)

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_user(client: TestClient, ioc: AsyncContainer):
    data = {"login": "bob", "password": "password_1"}
    response = client.post("/login", json=data)

    assert response.status_code == 200
    cookies = response.cookies
    assert "session_id" in cookies
    session_id = cookies["session_id"]
    redis_client: Redis = await ioc.get(Redis)
    result = await redis_client.get(session_id)
    assert result is not None


@pytest.mark.asyncio
async def test_login_not_exists_user(client: TestClient):
    data = {"login": "tom", "password": "password_1"}
    response = client.post("/login", json=data)

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_login_wrong_password(client: TestClient):
    data = {"login": "bob", "password": "password_2"}
    response = client.post("/login", json=data)

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: TestClient, ioc: AsyncContainer):
    data = {"login": "bob", "password": "password_1"}
    response = client.post("/login", json=data)
    session_id = response.cookies["session_id"]

    client.cookies.set(name="session_id", value=session_id)

    response = client.post("/logout")
    assert response.status_code == 200
    assert "session_id" not in response.cookies
    redis_client: Redis = await ioc.get(Redis)
    result = await redis_client.get(session_id)
    assert result is None


@pytest.mark.asyncio
async def test_search_location(client: TestClient):
    response = client.get("/search", params={"location_name": "Moscow"})
    assert response.status_code == 200
    assert len(response.json()) > 0


@pytest.mark.asyncio
async def test_search_not_exists_location(client: TestClient):
    response = client.get("/search", params={"location_name": "asdasdad"})
    assert response.status_code == 200
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_add_location(client: TestClient, ioc: AsyncContainer):
    data = {"login": "bob", "password": "password_1"}
    response = client.post("/login", json=data)
    assert response.status_code == 200

    data = {"name": "Moscow", "latitude": 55.7504461, "longitude": 37.6174943}
    session_id = response.cookies["session_id"]
    client.cookies.set(name="session_id", value=session_id)
    response = client.post("/search", json=data)
    assert response.status_code == 200

    session_maker: async_sessionmaker[AsyncSession] = await ioc.get(async_sessionmaker[AsyncSession])
    async with session_maker() as session:
        query = (
            select(LocationORM)
            .join(UserLocationORM, LocationORM.id == UserLocationORM.location_id)
            .join(UserORM, UserLocationORM.user_id == UserORM.id)
            .where(UserORM.login == "bob")
        )
        result = await session.scalars(query)
        assert result.first() is not None


@pytest.mark.asyncio
async def test_add_exists_location(client: TestClient, ioc: AsyncContainer):
    data = {"login": "bob", "password": "password_1"}
    response = client.post("/login", json=data)
    assert response.status_code == 200

    data = {"name": "Moscow", "latitude": 55.7504461, "longitude": 37.6174943}
    session_id = response.cookies["session_id"]
    client.cookies.set(name="session_id", value=session_id)
    response = client.post("/search", json=data)
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_get_locations(client: TestClient, ioc: AsyncContainer):
    data = {"login": "bob", "password": "password_1"}
    response = client.post("/login", json=data)
    assert response.status_code == 200

    session_id = response.cookies["session_id"]
    client.cookies.set(name="session_id", value=session_id)
    response = client.get("/locations")
    assert response.status_code == 200
    assert response.json()[0]["name"] == "Moscow"


@pytest.mark.asyncio
async def test_remove_location(client: TestClient, ioc: AsyncContainer):
    data = {"login": "bob", "password": "password_1"}
    response = client.post("/login", json=data)
    assert response.status_code == 200

    data = {"name": "Moscow", "latitude": 55.7504461, "longitude": 37.6174943}
    session_id = response.cookies["session_id"]
    client.cookies.set(name="session_id", value=session_id)
    response = client.delete("/", params=data)
    assert response.status_code == 200
