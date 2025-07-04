import asyncio
import logging

from fastapi import WebSocket, WebSocketDisconnect
from src.bot.domain.chat_bot import ChatBot
from src.bot.application.chat_bot_provider import ChatBotProvider
from src.bot.domain.services import ChatContextHistoryPoolServiceProvider
from src.core.domain.services import ConnectionManagerProvider
from src.core.infrastructure.thread_pool_provider import ThreadPoolProvider
from src.settings import Settings

logger = logging.getLogger(__name__)


class ChatHandlerWebsocket:
    def __init__(self, application_id: str, session_id: str, websocket: WebSocket):
        self._application_id: str = application_id
        self._session_id: str = session_id
        self._websocket: WebSocket = websocket
        self._settings: Settings = Settings.get()
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
        thread_pool = ThreadPoolProvider.get()
        try:
            while True:
                message = await self._websocket.receive_text()
                logging.info(
                    f"[{self._application_id}][{self._session_id}] Received: {message}"
                )

                context = await self._chat_history.get_context()
                if context is None:
                    context = self._get_initial_system_prompt()
                elif (len(context) - 1) > self._settings.bot_context_length:
                    context = self._generate_summary_of_current_context(context)

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

    def _get_initial_system_prompt(self) -> list[dict]:
        return [
            {
                "role": "system",
                "content": self._settings.bot_initial_system_prompt,
            }
        ]

    def _generate_summary_of_current_context(
        self, current_context: list[dict]
    ) -> list[dict]:
        logger.info(
            f"[{self._application_id}][{self._session_id}] Context exceeding {self._settings.bot_context_length}, clearing it up"
        )
        token_separator = "!!!__["
        context_summary = ""
        new_context = self._get_initial_system_prompt()
        for token in current_context:
            reply = token["content"]
            context_summary += f"{token_separator}{reply}"
        new_context += [
            {
                "role": "system",
                "content": f"Chat history reset, this is what you talked about so far "
                f"(each token message is separated by this string '{token_separator}') Context Summary:\n{context_summary}",
            }
        ]
        return new_context
