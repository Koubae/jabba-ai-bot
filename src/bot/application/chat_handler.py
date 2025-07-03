import os
import asyncio
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from fastapi import WebSocket, WebSocketDisconnect
from src.bot.domain.chat_bot import ChatBot
from src.bot.application.chat_bot_provider import ChatBotProvider
from src.bot.domain.services import ChatContextHistoryPoolServiceProvider


logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self._active_connections: dict[str, list[WebSocket]] = defaultdict(list)

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self._active_connections[session_id].append(websocket)

    def disconnect(self, websocket: WebSocket, session_id: str):
        self._active_connections[session_id].remove(websocket)

    async def send(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str, session_id: str):
        for connection in self._active_connections[session_id]:
            logger.debug(
                f"[{session_id}] Broadcasting message: {message} to connection {connection}"
            )
            await connection.send_text(message)


manager = ConnectionManager()
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
        await manager.connect(self._websocket, self._session_id)

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
                    manager.broadcast(reply, self._session_id),
                )
                await tasks

        except (WebSocketDisconnect, RuntimeError) as error:
            manager.disconnect(self._websocket, self._session_id)
            try:
                await manager.broadcast(
                    f"Client #USER_123 left the chat", self._session_id
                )
            except Exception as error_2:
                logger.warning(
                    f"[{self._application_id}][{self._session_id}] Error while broadcasting left chat message: {repr(error_2)}"
                )
            logging.info(
                f"[{self._application_id}][{self._session_id}] Client disconnected from session, error {repr(error)}"
            )
