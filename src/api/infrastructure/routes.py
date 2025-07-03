from fastapi import APIRouter
from redis.asyncio import Redis
import os
import uuid
import logging

from src.settings import Settings
from src.api.infrastructure.controllers import IndexController


def get_router() -> APIRouter:
    router = APIRouter()

    index_controller = IndexController()
    router.include_router(index_controller.router, tags=["index"])
    return router


# settings = Settings.get()
#
# logger = logging.getLogger(__name__)
# redis = Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_db)
#
# full_key = None
#
#
# @router.get("/")
# async def get_cache():
#     global full_key
#     if full_key is None:
#         return {"status": "error", "message": "Cache is empty"}
#     value = await redis.get(full_key)
#     logger.info("value from cache %s", value)
#     return {"key": full_key, "value": value.decode()}
#
#
# @router.post("/")
# async def set_cache():
#     global full_key
#     key = "hello-world"
#     value = "yooo" + str(uuid.uuid4())
#     ttl = 300
#     full_key = f"{settings.redis_service_prefix}:{key}"
#     await redis.set(full_key, value, ex=ttl)
#     return {"status": "success", "key": full_key}
