from datetime import timedelta
import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.limiter import limiter
from app.models import Board, Column, utcnow
from app.schemas import (
    BoardCreate, BoardCreated, BoardUpdate, BoardInfo,
    BoardFull, ColumnInfo, CardInfo,
)

router = APIRouter(prefix="/api/boards", tags=["boards"])

TEMPLATES = {
    "retrospective": [
        ("What went well", "green"),
        ("What to improve", "red"),
        ("Action items", "blue"),
    ],
    "4ls": [
        ("Liked", "green"),
        ("Learned", "blue"),
        ("Lacked", "red"),
        ("Longed For", "purple"),
    ],
}


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


async def get_board_or_404(board_id: str, db: AsyncSession) -> Board:
    result = await db.execute(select(Board).where(Board.id == board_id))
    board = result.scalar_one_or_none()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board


async def get_board_as_admin(board_id: str, admin_token: str, db: AsyncSession) -> Board:
    board = await get_board_or_404(board_id, db)
    if board.admin_token != admin_token:
        raise HTTPException(status_code=403, detail="Not authorized")
    return board


@router.post("", response_model=BoardCreated)
@limiter.limit("10/minute")
async def create_board(request: Request, payload: BoardCreate, db: AsyncSession = Depends(get_db)):
    """Create a new board with columns based on template."""
    password_hash = hash_password(payload.password) if payload.password else None

    board = Board(
        title=payload.title,
        description=payload.description,
        template=payload.template,
        ttl_hours=payload.ttl_hours,
        expires_at=utcnow() + timedelta(hours=payload.ttl_hours),
        password_hash=password_hash,
        is_readonly_default=payload.is_readonly_default,
    )
    db.add(board)
    await db.flush()  # need board.id before creating columns

    if payload.template == "custom" and payload.custom_columns:
        colors = ["green", "blue", "red", "purple"]
        for idx, col_title in enumerate(payload.custom_columns[:4]):
            db.add(Column(
                board_id=board.id,
                title=col_title.strip(),
                color=colors[idx % len(colors)],
                position=idx,
            ))
    elif payload.template in TEMPLATES:
        for idx, (col_title, color) in enumerate(TEMPLATES[payload.template]):
            db.add(Column(
                board_id=board.id,
                title=col_title,
                color=color,
                position=idx,
            ))

    return BoardCreated(board_id=board.id, admin_token=board.admin_token)


@router.get("/{board_id}", response_model=BoardFull)
@limiter.limit("10/minute")
async def get_board(
    request: Request,
    board_id: str,
    password: str | None = Query(None),
    admin_token: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Get full board with columns and cards."""
    result = await db.execute(
        select(Board)
        .where(Board.id == board_id)
        .options(selectinload(Board.columns).selectinload(Column.cards))
    )
    board = result.scalar_one_or_none()

    if not board:
        raise HTTPException(status_code=404, detail="Board not found")

    if board.expires_at < utcnow():
        raise HTTPException(status_code=410, detail="Board has expired")

    # Admin bypasses password check
    is_admin = admin_token and admin_token == board.admin_token
    if board.password_hash and not is_admin:
        if not password:
            raise HTTPException(status_code=401, detail="Password required")
        if not verify_password(password, board.password_hash):
            raise HTTPException(status_code=401, detail="Invalid password")

    columns_info = [ColumnInfo.model_validate(col) for col in board.columns]
    cards_info = [
        CardInfo.model_validate(card)
        for col in board.columns
        for card in col.cards
    ]

    return BoardFull(
        board=BoardInfo.from_board(board),
        columns=columns_info,
        cards=cards_info,
    )


@router.patch("/{board_id}", response_model=BoardInfo)
async def update_board(
    board_id: str,
    payload: BoardUpdate,
    admin_token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Update board settings (admin only)."""
    board = await get_board_as_admin(board_id, admin_token, db)

    if payload.title is not None:
        board.title = payload.title
    if payload.description is not None:
        board.description = payload.description
    if payload.is_readonly_default is not None:
        board.is_readonly_default = payload.is_readonly_default
    if payload.password is not None:
        board.password_hash = hash_password(payload.password) if payload.password else None

    return BoardInfo.from_board(board)


@router.delete("/{board_id}")
async def delete_board(
    board_id: str,
    admin_token: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Delete board and all associated data (admin only)."""
    board = await get_board_as_admin(board_id, admin_token, db)
    await db.delete(board)
    return {"detail": "Board deleted"}
