import logging
import asyncio
from sqlalchemy import delete
from app.database import async_session
from app.models import Board, utcnow

logger = logging.getLogger(__name__)


async def cleanup_expired_boards() -> None:
    """Delete boards that have passed their expires_at time."""
    async with async_session() as session:
        result = await session.execute(
            delete(Board).where(Board.expires_at < utcnow())
        )
        await session.commit()
        if result.rowcount > 0:
            logger.info("Cleaned up %d expired board(s)", result.rowcount)


def run_cleanup() -> None:
    """Synchronous wrapper for APScheduler."""
    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(cleanup_expired_boards())
    finally:
        loop.close()
