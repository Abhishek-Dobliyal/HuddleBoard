import json
import logging
import os
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import async_session, create_tables
from app.limiter import limiter
from app.models import Board, utcnow
from app.routers import boards, cards
from app.routers.boards import verify_password
from app.tasks import run_cleanup
from app.ws.manager import manager

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
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
        run_cleanup, "interval", minutes=cleanup_interval, id="ttl_cleanup"
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
    admin: str | None = Query(None),
    password: str | None = Query(None),
) -> None:
    async with async_session() as session:
        result = await session.execute(select(Board).where(Board.id == board_id))
        board = result.scalar_one_or_none()

    if not board:
        await websocket.close(code=4004, reason="Board not found")
        return

    if board.expires_at < utcnow():
        await websocket.close(code=4010, reason="Board has expired")
        return

    if board.password_hash:
        is_admin = admin is not None and admin == board.admin_token
        if not is_admin:
            if not password or not verify_password(password, board.password_hash):
                await websocket.close(code=4001, reason="Password required")
                return

    await manager.connect(websocket, board_id)
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
