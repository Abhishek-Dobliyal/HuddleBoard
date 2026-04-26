import uuid
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.constants import (
    UUID_LENGTH, TITLE_MAX_LENGTH, DESCRIPTION_MAX_LENGTH,
    COLUMN_NAME_MAX_LENGTH, AUTHOR_NAME_MAX_LENGTH,
    PASSWORD_HASH_MAX_LENGTH, DEFAULT_TTL_HOURS, DEFAULT_TEMPLATE,
    DEFAULT_AUTHOR, DEFAULT_CARD_COLOR,
)


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utcnow() -> datetime:
    """Naive UTC timestamp for SQLite compatibility."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Board(Base):
    __tablename__ = "boards"

    id: Mapped[str] = mapped_column(String(UUID_LENGTH), primary_key=True, default=generate_uuid)
    admin_token: Mapped[str] = mapped_column(String(UUID_LENGTH), default=generate_uuid, index=True)
    title: Mapped[str] = mapped_column(String(TITLE_MAX_LENGTH), nullable=False)
    description: Mapped[str] = mapped_column(String(DESCRIPTION_MAX_LENGTH), default="")
    template: Mapped[str] = mapped_column(String(COLUMN_NAME_MAX_LENGTH), default=DEFAULT_TEMPLATE)
    ttl_hours: Mapped[int] = mapped_column(Integer, default=DEFAULT_TTL_HOURS)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(PASSWORD_HASH_MAX_LENGTH), nullable=True, default=None)
    is_readonly_default: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    columns: Mapped[list["Column"]] = relationship(
        "Column", back_populates="board", cascade="all, delete-orphan",
        order_by="Column.position",
    )


class Column(Base):
    __tablename__ = "columns"

    id: Mapped[str] = mapped_column(String(UUID_LENGTH), primary_key=True, default=generate_uuid)
    board_id: Mapped[str] = mapped_column(String(UUID_LENGTH), ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(COLUMN_NAME_MAX_LENGTH), nullable=False)
    color: Mapped[str] = mapped_column(String(20), default="default")
    position: Mapped[int] = mapped_column(Integer, default=0)

    board: Mapped["Board"] = relationship("Board", back_populates="columns")
    cards: Mapped[list["Card"]] = relationship(
        "Card", back_populates="column", cascade="all, delete-orphan",
        order_by="Card.created_at",
    )


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[str] = mapped_column(String(UUID_LENGTH), primary_key=True, default=generate_uuid)
    column_id: Mapped[str] = mapped_column(String(UUID_LENGTH), ForeignKey("columns.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    author_name: Mapped[str] = mapped_column(String(AUTHOR_NAME_MAX_LENGTH), default=DEFAULT_AUTHOR)
    votes: Mapped[int] = mapped_column(Integer, default=0)
    color: Mapped[str] = mapped_column(String(20), default=DEFAULT_CARD_COLOR)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    column: Mapped["Column"] = relationship("Column", back_populates="cards")
