import logging
from collections import defaultdict
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.cache.application.get_cache import get_cache
from src.cache.domain.cache import Cache
from src.settings import Settings


logger = logging.getLogger(__name__)


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


class ChatHandler:
    def __init__(self, application_id: str, session_id: str, websocket: WebSocket):
        self._application_id: str = application_id
        self._session_id: str = session_id
        self._websocket: WebSocket = websocket
        self._active_connections: dict[str, list[WebSocket]] = {}

    async def handle(self) -> None:
        # await self._websocket.accept()
        await manager.connect(self._websocket, self._session_id)

        try:
            while True:
                data = await self._websocket.receive_text()
                logging.info(
                    f"[{self._application_id}][{self._session_id}] Received: {data}"
                )
                await manager.broadcast(
                    f"[{self._session_id}] >>> {data}", self._session_id
                )
        except (WebSocketDisconnect, RuntimeError):
            manager.disconnect(self._websocket, self._session_id)
            try:
                await manager.broadcast(
                    f"Client #USER_123 left the chat", self._session_id
                )
            except Exception as error:
                logger.warning(
                    f"[{self._application_id}][{self._session_id}] Error while broadcasting left chat message: {repr(error)}"
                )
            logging.info(
                f"[{self._application_id}][{self._session_id}] Client disconnected from session"
            )

        # self._active_connections.setdefault(self._session_id, []).append(
        #     self._websocket
        # )

    #     logging.info(
    #         f"[{self._application_id}][{self._session_id}] Client connected to session {self._session_id}"
    #     )
    #
    #     try:
    #         while True:
    #             data = await self._websocket.receive_text()
    #             logging.info(
    #                 f"[{self._application_id}][{self._session_id}] Received: {data}"
    #             )
    #             await self.broadcast(
    #                 self._session_id, f"[{self._session_id}] You said: {data}"
    #             )
    #     except WebSocketDisconnect:
    #         self._active_connections[self._session_id].remove(self._websocket)
    #         logging.info(
    #             f"[{self._application_id}][{self._session_id}] Client disconnected from session"
    #         )
    #
    # async def broadcast(self, session_id: str, message: str):
    #     for conn in self._active_connections.get(session_id, []):
    #         try:
    #             await conn.send_text(message)
    #         except WebSocketDisconnect:
    #             self._active_connections[self._session_id].remove(self._websocket)
    #             logging.info(
    #                 f"[{self._application_id}][{self._session_id}] Client disconnected (while broadcasting) from session"
    #             )
    #         except Exception as error:
    #             logging.info(
    #                 f"[{self._application_id}][{self._session_id}] Unknown Client error (while broadcasting) from session, error: {error}"
    #             )
