from typing import TypeVar, Protocol
from abc import ABC, abstractmethod

TCacheValue = TypeVar("TCacheValue", str, int, float, bool, dict, list)


class Cache(Protocol):
    async def get(self, key: str) -> TCacheValue:
        pass

    async def set(self, key: str, value: TCacheValue, ttl: int = 0) -> None:
        pass


class CacheFactory(ABC):
    @classmethod
    @abstractmethod
    def build(cls) -> Cache:
        pass

    @classmethod
    @abstractmethod
    def singleton(cls) -> Cache:
        pass
