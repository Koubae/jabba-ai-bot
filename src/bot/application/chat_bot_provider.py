import typing as t

from src.bot.domain.chat_bot import ChatBot
from src.bot.infrastructure.bots.chat_bot_testings import ChatBotTestingsMock
from src.bot.infrastructure.bots.ollama_chat_bots import (
    ChatBotOllamaOpenAI,
    ChatBotOllamaNeuralChat,
)
from src.settings import Settings


class ChatBotProvider:
    """Singleton Instance for Chat AI-Bot"""

    _singleton: t.ClassVar[t.Optional["ChatBot"]] = None

    @classmethod
    def get(cls) -> "ChatBot":
        if cls._singleton is None:
            ml_model = Settings.get().bot_ml_model
            match ml_model:  # noqa
                case "testings-mock":
                    chat_bot = ChatBotTestingsMock()
                case "openchat":
                    chat_bot = ChatBotOllamaOpenAI()
                case "neural-chat":
                    chat_bot = ChatBotOllamaNeuralChat()
                case _:
                    raise ValueError(f"Unsupported model: {ml_model}")
            cls._singleton = chat_bot
        return cls._singleton
