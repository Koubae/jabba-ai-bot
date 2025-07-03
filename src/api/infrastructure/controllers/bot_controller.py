import logging
import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.bot.application.chat_handler import ChatHandler
from src.cache.application.get_cache import get_cache
from src.cache.domain.cache import Cache
from src.settings import Settings


logger = logging.getLogger(__name__)


class BotController:
    def __init__(self):
        self.router: APIRouter = APIRouter()
        self.settings: Settings = Settings.get()
        self._register_routes()
        # self._cache: Cache = get_cache()

        # self.active_connections: dict[str, list[WebSocket]] = {}

    def _register_routes(self):
        self.router.add_api_websocket_route(
            path="/ws/bot/create-connection/{session_id}",
            endpoint=self.create_connection,
            name="AI-Bot Chat",
        )

    async def create_connection(self, websocket: WebSocket, session_id: str):
        application_id = "ai-bot"  # TODO: create a application_id!
        handler = ChatHandler(
            application_id=application_id, session_id=session_id, websocket=websocket
        )

        await handler.handle()
        logger.info(f"[{application_id}][{session_id}] All connections closed!")

        # import asyncio

        # task = asyncio.create_task(handler.handle())
        # asyncio.create_task(handler.handle())
        # await asyncio.sleep(3)
        # logger.info(
        #     f"[{application_id}][{session_id}] WebSocket connection initialized"
        # )
        #
        # await handler.handle()
        # logger.info(
        #     f"[{self._application_id}][{self._session_id}] All connections closed!"
        # )
