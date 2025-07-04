import asyncio
import logging

from fastapi import WebSocket, WebSocketDisconnect

from src.bot.application.bot_handler_base import BotHandlerBase
from src.core.domain.services import ConnectionManagerProvider

logger = logging.getLogger(__name__)


class BotHandlerCreateConnectionWebsocket(BotHandlerBase):
    def __init__(self, application_id: str, session_id: str, websocket: WebSocket):
        super().__init__(application_id, session_id)
        self._websocket: WebSocket = websocket

    async def handle(self) -> None:
        connection_manager = ConnectionManagerProvider.get()
        await connection_manager.connect(self._websocket, self._session_id)

        try:
            while True:
                message = await self._websocket.receive_text()
                logging.info(
                    f"[{self._application_id}][{self._session_id}] (WebSocket) Received: {message}"
                )

                context = await self._get_context()
                result = await self._process_bot_prompt(message, context)
                reply = result["reply"]
                context = result["context"]

                tasks = asyncio.gather(
                    self._chat_history.add_context(context),
                    connection_manager.broadcast(reply, self._session_id),
                )
                await tasks

        except (WebSocketDisconnect, RuntimeError) as error:
            connection_manager.disconnect(self._websocket, self._session_id)
            try:
                await connection_manager.broadcast(
                    f"Client #USER_123 left the chat", self._session_id
                )
            except Exception as error_2:
                logger.warning(
                    f"[{self._application_id}][{self._session_id}] (WebSocket) Error while broadcasting left chat message: {repr(error_2)}"
                )
            logging.info(
                f"[{self._application_id}][{self._session_id}] (WebSocket) Client disconnected from session, error {repr(error)}"
            )
