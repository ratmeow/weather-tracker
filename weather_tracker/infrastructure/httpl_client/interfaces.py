from abc import ABC, abstractmethod
from typing import Optional


class AsyncHTTPClient(ABC):
    def __init__(self, timeout):
        self.timeout = timeout

    @abstractmethod
    async def get(self, url: str, params: Optional[dict]) -> dict | list[dict]:
        pass

    @abstractmethod
    async def close(self):
        pass
