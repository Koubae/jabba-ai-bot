import typing as t

from src.bot.domain.services.chat_context_history_service import (
    ChatContextHistoryPoolService,
)


class ChatContextHistoryPoolServiceProvider:
    """Singleton Instance for ChatContextHistoryPoolService"""

    _singleton: t.ClassVar[t.Optional["ChatContextHistoryPoolService"]] = None

    @classmethod
    def get(cls) -> "ChatContextHistoryPoolService":
        if cls._singleton is None:
            chat_history_pool = ChatContextHistoryPoolService()
            cls._singleton = chat_history_pool
        return cls._singleton
