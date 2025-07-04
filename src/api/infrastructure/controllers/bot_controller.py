import logging

from fastapi import APIRouter, WebSocket
from pydantic import BaseModel

from src.bot.application.chat_handler_create_connection_websocket import (
    ChatHandlerCreateConnectionWebsocket,
)
from src.bot.application.chat_handler_send_message_http import (
    ChatHandlerSendMessageHttp,
)
from src.settings import Settings


logger = logging.getLogger(__name__)


class SendMessageHTTPRequest(BaseModel):
    message: str


class BotController:
    def __init__(self):
        self.router: APIRouter = APIRouter()
        self.settings: Settings = Settings.get()
        self._register_routes()

    def _register_routes(self):
        self.router.add_api_route(
            path="/http/bot/send-message/{session_id}",
            endpoint=self.send_message_http,
            name="AI-Bot Chat",
            methods=["POST"],
        )
        self.router.add_api_websocket_route(
            path="/ws/bot/create-connection/{session_id}",
            endpoint=self.create_connection_websocket,
            name="AI-Bot Chat Websocket Connection",
        )

    async def create_connection_websocket(self, websocket: WebSocket, session_id: str):
        application_id = "ai-bot"  # TODO: create a application_id!
        handler = ChatHandlerCreateConnectionWebsocket(
            application_id=application_id, session_id=session_id, websocket=websocket
        )

        await handler.handle()
        logger.info(
            f"[{application_id}][{session_id}] (WebSocket) All connections closed!"
        )

    async def send_message_http(
        self, session_id: str, request: SendMessageHTTPRequest
    ) -> dict:
        application_id = "ai-bot"  # TODO: create a application_id!

        handler = ChatHandlerSendMessageHttp(
            application_id=application_id, session_id=session_id
        )

        reply = await handler.handle(request.message)

        return {"reply": reply}
