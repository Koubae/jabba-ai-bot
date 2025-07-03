import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.cache.application.get_cache import get_cache
from src.cache.domain.cache import Cache
from src.settings import Settings


emitter_logger = logging.getLogger("emitter")
logger = logging.getLogger(__name__)


class BotController:
    def __init__(self):
        self.router: APIRouter = APIRouter()
        self.settings: Settings = Settings.get()
        self._register_routes()
        self._cache: Cache = get_cache()

        self.active_connections: dict[str, list[WebSocket]] = {}

    def _register_routes(self):
        self.router.add_api_websocket_route(
            path="/ws/bot/{session_id}",
            endpoint=self.websocket_endpoint,
            name="AI-Bot Chat",
        )

    async def websocket_endpoint(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections.setdefault(session_id, []).append(websocket)
        logging.info("Client connected to session %s", session_id)

        try:
            while True:
                data = await websocket.receive_text()
                logging.info(f"[{session_id}] Received: {data}")
                await self.broadcast(session_id, f"[{session_id}] You said: {data}")
        except WebSocketDisconnect:
            self.active_connections[session_id].remove(websocket)
            logging.info(f"Client disconnected from session {session_id}")

    async def broadcast(self, session_id: str, message: str):
        for conn in self.active_connections.get(session_id, []):
            try:
                await conn.send_text(message)
            except Exception:
                pass
