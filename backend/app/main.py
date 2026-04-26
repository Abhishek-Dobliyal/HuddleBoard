import os
import json
import logging
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.background import BackgroundScheduler

from app.database import create_tables
from app.routers import boards, cards
from app.ws.manager import manager
from app.tasks import run_cleanup

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
cleanup_interval = int(os.getenv("TTL_CLEANUP_INTERVAL_MINUTES", "30"))

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

    scheduler.add_job(run_cleanup, "interval", minutes=cleanup_interval, id="ttl_cleanup")
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

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in origins],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(boards.router)
app.include_router(cards.router)


@app.websocket("/ws/{board_id}")
async def websocket_endpoint(websocket: WebSocket, board_id: str) -> None:
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
                await manager.broadcast(board_id, {
                    "type": outgoing_type,
                    "data": msg_data,
                }, exclude=websocket)

    except WebSocketDisconnect:
        await manager.disconnect(websocket, board_id)
    except Exception:
        logger.error("WebSocket error on board %s", board_id, exc_info=True)
        await manager.disconnect(websocket, board_id)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "huddleboard"}
