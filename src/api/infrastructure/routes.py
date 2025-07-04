from fastapi import APIRouter

from src.api.infrastructure.controllers import IndexController, BotController


def get_router() -> APIRouter:
    router = APIRouter()

    index_controller = IndexController()
    router.include_router(index_controller.router, tags=["index"])

    bot_controller = BotController()
    router.include_router(bot_controller.router, prefix="/chat", tags=["bot"])

    return router
