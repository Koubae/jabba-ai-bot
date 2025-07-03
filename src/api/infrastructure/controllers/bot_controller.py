import logging

from fastapi import APIRouter, WebSocket

from src.bot.application.chat_handler import ChatHandler
from src.settings import Settings


logger = logging.getLogger(__name__)


class BotController:
    def __init__(self):
        self.router: APIRouter = APIRouter()
        self.settings: Settings = Settings.get()
        self._register_routes()

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
