import os
import asyncio
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

from fastapi import WebSocket, WebSocketDisconnect

from src.bot.domain.chat_bot import ChatBot
from src.bot.domain.services.chat_context_history_service import (
    ChatContextHistory,
    ChatContextHistoryPoolService,
)
from src.bot.infrastructure.bots.chat_bot_testings import ChatBotTestingsMock
from src.bot.infrastructure.bots.ollama_chat_bots import (
    ChatBotOllamaOpenAI,
    ChatBotOllamaNeuralChat,
)
from src.settings import Settings


logger = logging.getLogger(__name__)

chat_history_pool = ChatContextHistoryPoolService()


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

chat_bot_mock = ChatBotTestingsMock()
chat_bot_open_api = ChatBotOllamaOpenAI()
chat_bot_neural_chat = ChatBotOllamaNeuralChat()


def get_chat_bot(settings: Settings) -> ChatBot:
    ml_model = settings.bot_ml_model
    match ml_model:  # noqa
        case "testings-mock":
            return chat_bot_mock
        case "openchat":
            return chat_bot_open_api
        case "neural-chat":
            return chat_bot_neural_chat
        case _:
            raise ValueError(f"Unsupported model: {ml_model}")


class ChatHandler:
    def __init__(self, application_id: str, session_id: str, websocket: WebSocket):
        self._application_id: str = application_id
        self._session_id: str = session_id
        self._websocket: WebSocket = websocket
        self._active_connections: dict[str, list[WebSocket]] = {}
        self._chat_history: ChatContextHistory = (
            chat_history_pool.get_or_create_history(application_id, session_id)
        )

    async def handle(self) -> None:
        await manager.connect(self._websocket, self._session_id)

        loop = asyncio.get_event_loop()
        bot = get_chat_bot(Settings.get())
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
                    bot.chat,
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
