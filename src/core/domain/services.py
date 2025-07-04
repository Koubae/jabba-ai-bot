import logging
import typing as t
from collections import defaultdict

from src.core.domain.interfaces import IWebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self._active_connections: dict[str, list[IWebSocket]] = defaultdict(list)

    async def connect(self, websocket: IWebSocket, session_id: str) -> None:
        await websocket.accept()
        self._active_connections[session_id].append(websocket)

    def disconnect(self, websocket: IWebSocket, session_id: str) -> None:
        self._active_connections[session_id].remove(websocket)

    async def send(self, message: str, websocket: IWebSocket) -> None:
        await websocket.send_text(message)

    async def broadcast(self, message: str, session_id: str) -> None:
        for connection in self._active_connections[session_id]:
            logger.debug(
                f"[{session_id}] Broadcasting message: {message} to connection {connection}"
            )
            await connection.send_text(message)


class ConnectionManagerProvider:
    """Singleton Instance for ConnectionManager"""

    _singleton: t.ClassVar[t.Optional["ConnectionManager"]] = None

    @classmethod
    def get(cls) -> "ConnectionManager":
        if cls._singleton is None:
            singleton = ConnectionManager()
            cls._singleton = singleton
        return cls._singleton
