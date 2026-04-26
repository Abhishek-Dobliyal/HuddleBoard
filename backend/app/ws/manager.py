import json
import logging
from collections import defaultdict
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections per board room."""

    def __init__(self) -> None:
        self.rooms: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, websocket: WebSocket, board_id: str) -> None:
        await websocket.accept()
        self.rooms[board_id].add(websocket)
        count = len(self.rooms[board_id])
        await self.broadcast(board_id, {
            "type": "user:joined",
            "data": {"count": count},
        })
        logger.info("WS connected to board %s (%d users)", board_id, count)

    async def disconnect(self, websocket: WebSocket, board_id: str) -> None:
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

    async def broadcast(
        self, board_id: str, message: dict, exclude: WebSocket | None = None
    ) -> None:
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

        if dead_connections:
            for ws in dead_connections:
                self.rooms[board_id].discard(ws)
                logger.warning("Removed dead WS from board %s", board_id)

            # Re-broadcast corrected user count to remaining live sockets
            if board_id in self.rooms and self.rooms[board_id]:
                corrected_count = len(self.rooms[board_id])
                corrected_data = json.dumps({
                    "type": "user:left",
                    "data": {"count": corrected_count},
                }, default=str)
                for ws in list(self.rooms[board_id]):
                    try:
                        await ws.send_text(corrected_data)
                    except Exception:
                        self.rooms[board_id].discard(ws)
            elif board_id in self.rooms:
                del self.rooms[board_id]


manager = ConnectionManager()
