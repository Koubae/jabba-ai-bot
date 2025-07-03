from redis.asyncio import Redis, ConnectionPool

from src.settings import Settings
from src.cache.domain.cache import Cache, CacheFactory


class CacheRedis(Cache):
    pass


class RedisCacheFactory(CacheFactory):
    client: Redis = None

    @classmethod
    def build(cls) -> Cache:
        return cls.singleton()

    @classmethod
    def singleton(cls) -> Cache:
        if cls.client is not None:
            return cls.client

        settings = Settings.get()
        pool = ConnectionPool(
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            max_connections=settings.redis_max_connections,
        )
        cls.client = Redis(connection_pool=pool)
        return cls.client
