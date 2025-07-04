from abc import ABC, abstractmethod

from src.bot.domain.dto import ChatBotReply


class ChatBot(ABC):
    @property
    @abstractmethod
    def _model(self) -> str:
        pass

    @abstractmethod
    def chat(self, prompt: str, context: list[dict]) -> ChatBotReply:
        pass
