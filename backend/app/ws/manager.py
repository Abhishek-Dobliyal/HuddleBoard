import json
import logging
from collections import defaultdict
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections per board room."""

    def __init__(self):
        self.rooms: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, board_id: str):
        await websocket.accept()
        self.rooms[board_id].add(websocket)
        count = len(self.rooms[board_id])
        await self.broadcast(board_id, {
            "type": "user:joined",
            "data": {"count": count},
        })
        logger.info("WS connected to board %s (%d users)", board_id, count)

    async def disconnect(self, websocket: WebSocket, board_id: str):
        self.rooms[board_id].discard(websocket)
        count = len(self.rooms[board_id])
        if count == 0:
            del self.rooms[board_id]
        else:
            await self.broadcast(board_id, {
                "type": "user:left",
                "data": {"count": count},
            })
        logger.info("WS disconnected from board %s (%d remaining)", board_id, count)

    async def broadcast(self, board_id: str, message: dict, exclude: WebSocket | None = None):
        """Send a message to all connections in a board room."""
        if board_id not in self.rooms:
            return

        data = json.dumps(message, default=str)
        dead_connections = set()

        for ws in self.rooms[board_id]:
            if ws == exclude:
                continue
            try:
                await ws.send_text(data)
            except Exception:
                dead_connections.add(ws)

        for ws in dead_connections:
            self.rooms[board_id].discard(ws)


manager = ConnectionManager()
