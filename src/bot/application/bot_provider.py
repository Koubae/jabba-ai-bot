import typing as t

from src.bot.domain.ai_bot import AIBot
from src.bot.infrastructure.bots.chat_bot_testings import AIBotTestingsMock
from src.bot.infrastructure.bots.ollama_chat_bots import (
    AIBotOllamaOpenAI,
    AIBotOllamaNeuralChat,
)
from src.settings import Settings


class BotProvider:
    """Singleton Instance for AI-Bot"""

    _singleton: t.ClassVar[t.Optional["AIBot"]] = None

    @classmethod
    def get(cls) -> "AIBot":
        if cls._singleton is None:
            ml_model = Settings.get().bot_ml_model
            match ml_model:  # noqa
                case "testings-mock":
                    chat_bot = AIBotTestingsMock()
                case "openchat":
                    chat_bot = AIBotOllamaOpenAI()
                case "neural-chat":
                    chat_bot = AIBotOllamaNeuralChat()
                case _:
                    raise ValueError(f"Unsupported model: {ml_model}")
            cls._singleton = chat_bot
        return cls._singleton
