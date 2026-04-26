import asyncio
import json
import logging
import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.constants import (
    WS_CLOSE_BOARD_NOT_FOUND, WS_CLOSE_BOARD_EXPIRED,
    WS_CLOSE_PASSWORD_REQUIRED, WS_AUTH_TIMEOUT_SECONDS,
)
from app.database import async_session, create_tables
from app.limiter import limiter
from app.models import Board, utcnow
from app.routers import boards, cards
from app.routers.boards import verify_password
from app.tasks import cleanup_expired_boards
from app.ws.manager import manager

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
cleanup_interval = int(os.getenv("TTL_CLEANUP_INTERVAL_MINUTES", "15"))

WS_EVENT_MAP: dict[str, str] = {
    "card:add": "card:added",
    "card:update": "card:updated",
    "card:delete": "card:deleted",
    "card:vote": "card:voted",
    "card:move": "card:moved",
    "board:update": "board:updated",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    logger.info("Database tables created")

    scheduler.add_job(
        cleanup_expired_boards, "interval", minutes=cleanup_interval, id="ttl_cleanup"
    )
    scheduler.start()
    logger.info("TTL cleanup scheduler started (every %d min)", cleanup_interval)

    yield

    scheduler.shutdown()
    logger.info("Scheduler stopped")


app = FastAPI(
    title="HuddleBoard API",
    version="0.1.0",
    lifespan=lifespan,
)

origins_env = os.getenv("CORS_ORIGINS", "")
origins = [o.strip() for o in origins_env.split(",") if o.strip()] if origins_env else ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if "*" not in origins else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(boards.router)
app.include_router(cards.router)


@app.websocket("/ws/{board_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    board_id: str,
) -> None:
    async with async_session() as session:
        result = await session.execute(select(Board).where(Board.id == board_id))
        board = result.scalar_one_or_none()

    if not board:
        await websocket.close(code=WS_CLOSE_BOARD_NOT_FOUND, reason="Board not found")
        return

    if board.expires_at < utcnow():
        await websocket.close(code=WS_CLOSE_BOARD_EXPIRED, reason="Board has expired")
        return

    # Accept the connection, then authenticate via first message
    await websocket.accept()

    if board.password_hash:
        try:
            raw = await asyncio.wait_for(
                websocket.receive_text(), timeout=WS_AUTH_TIMEOUT_SECONDS,
            )
            auth_msg = json.loads(raw)
        except (asyncio.TimeoutError, json.JSONDecodeError, Exception):
            await websocket.close(code=WS_CLOSE_PASSWORD_REQUIRED, reason="Auth timeout")
            return

        if auth_msg.get("type") != "auth":
            await websocket.close(code=WS_CLOSE_PASSWORD_REQUIRED, reason="Expected auth message")
            return

        admin_token = auth_msg.get("data", {}).get("adminToken")
        password = auth_msg.get("data", {}).get("password")

        is_admin = admin_token is not None and admin_token == board.admin_token
        if not is_admin:
            if not password or not verify_password(password, board.password_hash):
                await websocket.close(code=WS_CLOSE_PASSWORD_REQUIRED, reason="Password required")
                return

    # Auth passed — add to room
    board_id_str = board_id
    self_rooms = manager.rooms
    self_rooms[board_id_str].add(websocket)
    count = len(self_rooms[board_id_str])
    await manager.broadcast(board_id_str, {
        "type": "user:joined",
        "data": {"count": count},
    })
    logger.info("WS connected to board %s (%d users)", board_id_str, count)

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                continue

            if not isinstance(message, dict):
                continue

            msg_type = message.get("type")
            msg_data = message.get("data", {})

            outgoing_type = WS_EVENT_MAP.get(msg_type)
            if outgoing_type:
                await manager.broadcast(
                    board_id,
                    {
                        "type": outgoing_type,
                        "data": msg_data,
                    },
                    exclude=websocket,
                )

    except WebSocketDisconnect:
        await manager.disconnect(websocket, board_id)
    except Exception:
        logger.error("WebSocket error on board %s", board_id, exc_info=True)
        await manager.disconnect(websocket, board_id)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "huddleboard"}
