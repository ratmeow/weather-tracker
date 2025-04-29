import random
from typing import Optional

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from weather_tracker.infrastructure.httpl_client.exceptions import AsyncClientInternalError
from weather_tracker.infrastructure.httpl_client.interfaces import AsyncHTTPClient


class MockAsyncHTTPClient(AsyncHTTPClient):
    async def get(self, url: str, params: Optional[dict]) -> dict | list[dict]:
        if "location" in url:
            if len(params["q"]) == 0:
                raise AsyncClientInternalError
            if "Ufa" in params["q"]:
                return [
                    {"name": params["q"], "lattt": random.random() * 100, "lon": random.random() * 100}
                    for i in range(random.randint(1, 5))
                ]
            return [
                {"name": params["q"], "lat": random.random() * 100, "lon": random.random() * 100}
                for i in range(random.randint(1, 5))
            ]

        if "weather" in url:
            if params["lat"] < 0 or params["lon"] < 0:
                raise AsyncClientInternalError
            if params["lat"] == params["lon"]:
                return [{}]
            return {"main": {"temp": 10}}

        return []

    async def close(self):
        pass


class MockDatabase:
    def __init__(self, db_url: str):
        self.engine = create_async_engine(url=db_url)
        self.async_session_maker = async_sessionmaker(self.engine, expire_on_commit=False)
