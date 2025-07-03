from typing import Type
from src.cache.domain.cache import Cache, CacheFactory
from src.cache.infrastructure.cache_builder import RedisCacheFactory
from src.settings import Settings


def get_cache() -> Cache:
    factory = get_cache_factory()
    return factory.singleton()


def get_cache_factory() -> Type[CacheFactory]:
    cache_backend = Settings.get().cache_backend

    match cache_backend:  # noqa
        case "redis":
            return RedisCacheFactory
        case _:
            raise NotImplementedError(
                f"Cache backend {cache_backend} is not implemented"
            )
