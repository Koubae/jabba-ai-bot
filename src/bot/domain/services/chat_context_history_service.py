import json

from src.cache.application.cache_provider import get_cache
from src.cache.domain.cache import Cache
from src.settings import Settings


class ChatContextHistory:
    def __init__(self, application_id: str, session_id: str):
        self._application_id = application_id
        self._session_id = session_id
        self._settings: Settings = Settings.get()
        self._cache: Cache = get_cache()

        self._cache_key = f"{self._settings.cache_service_prefix}{self._application_id}:{self._session_id}"

    async def add_context(self, context: list[dict]) -> None:
        context_encoded = json.dumps(context)
        await self._cache.set(self._cache_key, context_encoded, ex=300)

    async def get_context(self) -> list[dict] | None:
        cached = await self._cache.get(self._cache_key)
        if cached is None:
            return None
        history = json.loads(cached)
        return history


class ChatContextHistoryPoolService:
    def __init__(self):
        self._sessions: dict[tuple[str, str], ChatContextHistory] = {}

    def create_history(
        self, application_id: str, session_id: str
    ) -> ChatContextHistory:
        chat_history = ChatContextHistory(application_id, session_id)
        self._sessions[(application_id, session_id)] = chat_history
        return chat_history

    def get_history(
        self, application_id: str, session_id: str
    ) -> ChatContextHistory | None:
        return self._sessions.get((application_id, session_id), None)

    def get_or_create_history(
        self, application_id: str, session_id: str
    ) -> ChatContextHistory:
        chat_history = self._sessions.get((application_id, session_id), None)
        if chat_history is None:
            chat_history = self.create_history(application_id, session_id)
        return chat_history

    def remove_history(self, application_id: str, session_id: str) -> None:
        del self._sessions[(application_id, session_id)]
