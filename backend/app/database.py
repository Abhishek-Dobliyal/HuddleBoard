import os
import ssl as ssl_mod
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

load_dotenv()

def _build_db_url() -> str:
    """Convert DATABASE_URL env var to an async SQLAlchemy-compatible URL."""
    url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./huddleboard.db")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    # asyncpg doesn't understand sslmode param — strip it
    if "sslmode=" in url:
        url = url.split("?")[0]
    return url

DATABASE_URL = _build_db_url()
is_sqlite = DATABASE_URL.startswith("sqlite")
is_postgres = DATABASE_URL.startswith("postgresql")

# asyncpg needs ssl passed via connect_args, not URL
pg_connect_args = {}
if is_postgres:
    ctx = ssl_mod.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl_mod.CERT_NONE
    pg_connect_args = {"ssl": ctx}

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if is_sqlite else pg_connect_args,
    # Postgres connection pool settings
    **({} if is_sqlite else {"pool_size": 10, "max_overflow": 20}),
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    """Dependency: yields an async database session."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def create_tables() -> None:
    """Create all tables on startup (dev/fallback only — use Alembic in prod)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
