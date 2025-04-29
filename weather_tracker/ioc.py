from typing import AsyncIterable
from uuid import UUID

from dishka import AnyOf, Provider, Scope, from_context, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from weather_tracker.application.interfaces import (
    DBSession,
    Hasher,
    LocationGateway,
    UserGateway,
    UserSessionGateway,
    WeatherClient,
)
from weather_tracker.application.use_cases import (
    AddUserLocation,
    GetUserLocations,
    LoginUser,
    LogoutUser,
    RegisterUser,
    RemoveUserLocation,
    SearchLocation,
)
from weather_tracker.config import Config
from weather_tracker.infrastructure.database.gateways import PgOrmLocationGateway, PgOrmUserGateway
from weather_tracker.infrastructure.database.session import pg_session_maker
from weather_tracker.infrastructure.external_api.open_weather_client import OpenWeatherClient
from weather_tracker.infrastructure.hash_service import BcryptHasher
from weather_tracker.infrastructure.httpl_client.aiohttp_client import (
    AiohttpClient,
    AsyncHTTPClient,
)
from weather_tracker.infrastructure.session_gateway import RedisUserSessionGateway


class AppProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)

    @provide(scope=Scope.APP)
    async def get_redis(self, config: Config) -> AsyncIterable[Redis]:
        redis = Redis(host=config.redis.host, port=config.redis.port)
        try:
            yield redis
        finally:
            await redis.aclose()

    @provide(scope=Scope.APP)
    async def get_async_http_client(self) -> AsyncIterable[AsyncHTTPClient]:
        client = AiohttpClient(timeout=60)
        try:
            yield client
        finally:
            await client.close()

    @provide(scope=Scope.APP)
    def get_weather_client(self, http_client: AsyncHTTPClient, config: Config) -> WeatherClient:
        return OpenWeatherClient(async_http_client=http_client, config=config.open_weather)

    @provide(scope=Scope.APP)
    def get_session_maker(self, config: Config) -> async_sessionmaker[AsyncSession]:
        return pg_session_maker(pg_config=config.postgres)

    @provide(scope=Scope.REQUEST)
    async def get_session(
        self, session_maker: async_sessionmaker[AsyncSession]
    ) -> AsyncIterable[AnyOf[AsyncSession, DBSession]]:
        async with session_maker() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    def get_user_gateway(self, session: AsyncSession) -> UserGateway:
        return PgOrmUserGateway(session=session)

    @provide(scope=Scope.REQUEST)
    def get_location_gateway(self, session: AsyncSession) -> LocationGateway:
        return PgOrmLocationGateway(session=session)

    @provide(scope=Scope.APP)
    def get_hasher(self) -> Hasher:
        return BcryptHasher()

    @provide(scope=Scope.REQUEST)
    def get_user_session_gateway(self, redis_client: Redis, config: Config) -> UserSessionGateway:
        return RedisUserSessionGateway(redis_client=redis_client, config=config.redis)

    register_user = provide(RegisterUser, scope=Scope.REQUEST)
    login_user = provide(LoginUser, scope=Scope.REQUEST)
    logout_user = provide(LogoutUser, scope=Scope.REQUEST)
    search_location = provide(SearchLocation, scope=Scope.REQUEST)
    add_location = provide(AddUserLocation, scope=Scope.REQUEST)
    remove_location = provide(RemoveUserLocation, scope=Scope.REQUEST)
    get_locations = provide(GetUserLocations, scope=Scope.REQUEST)
