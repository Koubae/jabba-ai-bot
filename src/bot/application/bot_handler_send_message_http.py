import logging

from src.bot.application.bot_handler_base import BotHandlerBase

logger = logging.getLogger(__name__)


class BotHandlerSendMessageHttp(BotHandlerBase):
    async def handle(self, message: str) -> str:
        logging.info(
            f"[{self._application_id}][{self._session_id}] Received: {message}"
        )

        context = await self._get_context()
        result = await self._process_bot_prompt(message, context)

        reply = result["reply"]
        context = result["context"]
        await self._chat_history.add_context(context)

        return reply
