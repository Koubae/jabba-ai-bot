import asyncio
import logging
from asyncio import AbstractEventLoop

from src.bot.domain.dto import ChatBotReply
from src.settings import Settings
from src.bot.domain.chat_bot import ChatBot
from src.bot.application.chat_bot_provider import ChatBotProvider
from src.bot.domain.services import ChatContextHistoryPoolServiceProvider
from src.core.infrastructure.thread_pool_provider import ThreadPoolProvider

logger = logging.getLogger(__name__)


class ChatHandlerBase:
    def __init__(self, application_id: str, session_id: str):
        self._application_id: str = application_id
        self._session_id: str = session_id
        self._settings: Settings = Settings.get()
        self._chat_history = (
            ChatContextHistoryPoolServiceProvider.get().get_or_create_history(
                application_id, session_id
            )
        )
        self._bot: ChatBot = ChatBotProvider.get()
        self._loop: AbstractEventLoop = asyncio.get_event_loop()
        self._thread_pool = ThreadPoolProvider.get()

    def _get_initial_system_prompt(self) -> list[dict]:
        return [
            {
                "role": "system",
                "content": self._settings.bot_initial_system_prompt,
            }
        ]

    async def _get_context(self) -> list[dict]:
        context = await self._chat_history.get_context()
        if context is None:
            context = self._get_initial_system_prompt()
        elif (len(context) - 1) > self._settings.bot_context_length:
            context = self._generate_summary_of_current_context(context)
        return context

    async def _process_bot_prompt(
        self, message: str, context: list[dict]
    ) -> ChatBotReply:
        result = await self._loop.run_in_executor(
            self._thread_pool,
            self._bot.chat,
            message,
            context,
        )
        return result

    def _generate_summary_of_current_context(
        self, current_context: list[dict]
    ) -> list[dict]:
        logger.info(
            f"[{self._application_id}][{self._session_id}] (WebSocket) Context exceeding {self._settings.bot_context_length}, clearing it up"
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
