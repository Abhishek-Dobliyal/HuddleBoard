from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.limiter import limiter
from app.models import Card, Column, utcnow
from app.schemas import CardCreate, CardUpdate, CardMove, CardInfo

router = APIRouter(tags=["cards"])


def is_board_admin(board, admin_token: str | None) -> bool:
    return admin_token is not None and admin_token == board.admin_token


async def get_card_with_board(card_id: str, db: AsyncSession) -> Card:
    """Load a card with its column and board eagerly."""
    result = await db.execute(
        select(Card)
        .where(Card.id == card_id)
        .options(selectinload(Card.column).selectinload(Column.board))
    )
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


def assert_not_expired(board) -> None:
    if board.expires_at < utcnow():
        raise HTTPException(status_code=410, detail="Board has expired")


def assert_writable(board, admin_token: str | None) -> None:
    if board.is_readonly_default and not is_board_admin(board, admin_token):
        raise HTTPException(status_code=403, detail="Board is read-only")


@router.post("/api/boards/{board_id}/cards", response_model=CardInfo)
async def create_card(
    board_id: str,
    payload: CardCreate,
    admin_token: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> CardInfo:
    """Add a card to a column on a board."""
    result = await db.execute(
        select(Column)
        .where(Column.id == payload.column_id, Column.board_id == board_id)
        .options(selectinload(Column.board))
    )
    column = result.scalar_one_or_none()
    if not column:
        raise HTTPException(status_code=404, detail="Column not found on this board")

    assert_not_expired(column.board)
    assert_writable(column.board, admin_token)

    card = Card(
        column_id=payload.column_id,
        text=payload.text,
        author_name=payload.author_name,
        color=payload.color,
    )
    db.add(card)
    await db.flush()
    return CardInfo.model_validate(card)


@router.patch("/api/cards/{card_id}", response_model=CardInfo)
async def update_card(
    card_id: str,
    payload: CardUpdate,
    admin_token: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> CardInfo:
    """Update card text."""
    card = await get_card_with_board(card_id, db)
    assert_not_expired(card.column.board)
    assert_writable(card.column.board, admin_token)

    card.text = payload.text
    return CardInfo.model_validate(card)


@router.patch("/api/cards/{card_id}/move", response_model=CardInfo)
async def move_card(
    card_id: str,
    payload: CardMove,
    admin_token: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> CardInfo:
    """Move a card to a different column."""
    card = await get_card_with_board(card_id, db)
    source_board_id = card.column.board_id

    result = await db.execute(
        select(Column)
        .where(Column.id == payload.column_id)
        .options(selectinload(Column.board))
    )
    target_column = result.scalar_one_or_none()
    if not target_column:
        raise HTTPException(status_code=404, detail="Target column not found")

    if source_board_id != target_column.board_id:
        raise HTTPException(status_code=400, detail="Cannot move card across boards")

    assert_not_expired(target_column.board)
    assert_writable(target_column.board, admin_token)

    card.column_id = payload.column_id
    return CardInfo.model_validate(card)


@router.delete("/api/cards/{card_id}")
async def delete_card(
    card_id: str,
    admin_token: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
) -> dict[str, str]:
    """Delete a card."""
    card = await get_card_with_board(card_id, db)
    assert_not_expired(card.column.board)
    assert_writable(card.column.board, admin_token)

    await db.delete(card)
    return {"detail": "Card deleted"}


@router.post("/api/cards/{card_id}/vote", response_model=CardInfo)
@limiter.limit("30/minute")
async def vote_card(
    request: Request,
    card_id: str,
    db: AsyncSession = Depends(get_db),
) -> CardInfo:
    """Increment vote count on a card (atomic)."""
    card = await get_card_with_board(card_id, db)
    assert_not_expired(card.column.board)

    await db.execute(
        update(Card).where(Card.id == card_id).values(votes=Card.votes + 1)
    )
    await db.refresh(card)
    return CardInfo.model_validate(card)
