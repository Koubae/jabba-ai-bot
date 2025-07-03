import os
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from fastapi import WebSocket, WebSocketDisconnect
from src.bot.domain.chat_bot import ChatBot
from src.bot.application.chat_bot_provider import ChatBotProvider
from src.bot.domain.services import ChatContextHistoryPoolServiceProvider
from src.core.domain.services import ConnectionManagerProvider

logger = logging.getLogger(__name__)


MAX_WORKERS = 20
thread_pool = ThreadPoolExecutor(max_workers=min(os.cpu_count(), MAX_WORKERS))


class ChatHandler:
    def __init__(self, application_id: str, session_id: str, websocket: WebSocket):
        self._application_id: str = application_id
        self._session_id: str = session_id
        self._websocket: WebSocket = websocket
        self._active_connections: dict[str, list[WebSocket]] = {}
        self._chat_history = (
            ChatContextHistoryPoolServiceProvider.get().get_or_create_history(
                application_id, session_id
            )
        )
        self._bot: ChatBot = ChatBotProvider.get()

    async def handle(self) -> None:
        connection_manager = ConnectionManagerProvider.get()
        await connection_manager.connect(self._websocket, self._session_id)

        loop = asyncio.get_event_loop()
        try:
            while True:
                message = await self._websocket.receive_text()
                logging.info(
                    f"[{self._application_id}][{self._session_id}] Received: {message}"
                )

                context = await self._chat_history.get_context()
                if context is None:
                    context = [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant, listen to the user and respond clearly.",
                        }
                    ]

                result = await loop.run_in_executor(
                    thread_pool,
                    self._bot.chat,
                    message,
                    context,
                )

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
                    f"[{self._application_id}][{self._session_id}] Error while broadcasting left chat message: {repr(error_2)}"
                )
            logging.info(
                f"[{self._application_id}][{self._session_id}] Client disconnected from session, error {repr(error)}"
            )
