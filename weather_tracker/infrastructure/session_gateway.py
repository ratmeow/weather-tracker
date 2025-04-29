import logging
import uuid
from datetime import UTC, datetime, timedelta
from uuid import UUID

from redis.asyncio import Redis

from weather_tracker.application.dto import UserSessionDTO
from weather_tracker.application.interfaces import UserSessionGateway
from weather_tracker.config import RedisConfig

logger = logging.getLogger(__name__)


class RedisInternalError(Exception):
    pass


class SessionNotFoundError(Exception):
    pass


class RedisUserSessionGateway(UserSessionGateway):
    def __init__(self, redis_client: Redis, config: RedisConfig):
        self.redis_client = redis_client
        self.lifetime = config.session_lifetime

    async def create(self, user_id: UUID) -> UserSessionDTO:
        session_id = uuid.uuid4()
        try:
            await self.redis_client.setex(
                name=str(session_id), time=timedelta(seconds=self.lifetime), value=str(user_id)
            )
            return UserSessionDTO(
                session_id=session_id, user_id=user_id, expired_ts=datetime.now(UTC) + timedelta(seconds=self.lifetime)
            )
        except Exception as e:
            logger.error(e)
            raise RedisInternalError

    async def get_user_id(self, session_id: UUID) -> UUID:
        try:
            result = await self.redis_client.get(str(session_id))
        except Exception as e:
            logger.error(e)
            raise RedisInternalError
        if result is None:
            raise SessionNotFoundError
        return UUID(result.decode())

    async def delete(self, session_id: UUID) -> None:
        try:
            await self.redis_client.delete(str(session_id))
        except Exception as e:
            logger.error(e)
            raise RedisInternalError
