from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Board, Card, Column, utcnow
from app.schemas import CardCreate, CardUpdate, CardMove, CardInfo

router = APIRouter(tags=["cards"])


async def get_card_or_404(card_id: str, db: AsyncSession) -> Card:
    result = await db.execute(select(Card).where(Card.id == card_id))
    card = result.scalar_one_or_none()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card


async def check_board_admin(board: Board, admin_token: str | None) -> bool:
    """Return True if the request is from the board admin."""
    return admin_token is not None and admin_token == board.admin_token


@router.post("/api/boards/{board_id}/cards", response_model=CardInfo)
async def create_card(
    board_id: str,
    payload: CardCreate,
    admin_token: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Add a card to a column on a board."""
    result = await db.execute(
        select(Column)
        .where(Column.id == payload.column_id, Column.board_id == board_id)
        .options(selectinload(Column.board))
    )
    column = result.scalar_one_or_none()

    if not column:
        raise HTTPException(status_code=404, detail="Column not found on this board")

    if column.board.expires_at < utcnow():
        raise HTTPException(status_code=410, detail="Board has expired")

    is_admin = await check_board_admin(column.board, admin_token)
    if column.board.is_readonly_default and not is_admin:
        raise HTTPException(status_code=403, detail="Board is read-only")

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
    db: AsyncSession = Depends(get_db),
):
    """Update card text."""
    card = await get_card_or_404(card_id, db)
    card.text = payload.text
    return CardInfo.model_validate(card)


@router.patch("/api/cards/{card_id}/move", response_model=CardInfo)
async def move_card(
    card_id: str,
    payload: CardMove,
    admin_token: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """Move a card to a different column."""
    card = await get_card_or_404(card_id, db)

    # Verify target column exists and is on the same board
    result = await db.execute(
        select(Column)
        .where(Column.id == payload.column_id)
        .options(selectinload(Column.board))
    )
    target_column = result.scalar_one_or_none()

    if not target_column:
        raise HTTPException(status_code=404, detail="Target column not found")

    # Get source column to verify same board
    source_result = await db.execute(
        select(Column).where(Column.id == card.column_id)
    )
    source_column = source_result.scalar_one_or_none()

    if not source_column or source_column.board_id != target_column.board_id:
        raise HTTPException(status_code=400, detail="Cannot move card across boards")

    is_admin = await check_board_admin(target_column.board, admin_token)
    if target_column.board.is_readonly_default and not is_admin:
        raise HTTPException(status_code=403, detail="Board is read-only")

    card.column_id = payload.column_id
    return CardInfo.model_validate(card)


@router.delete("/api/cards/{card_id}")
async def delete_card(
    card_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete a card."""
    card = await get_card_or_404(card_id, db)
    await db.delete(card)
    return {"detail": "Card deleted"}


@router.post("/api/cards/{card_id}/vote", response_model=CardInfo)
async def vote_card(
    card_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Increment vote count on a card."""
    card = await get_card_or_404(card_id, db)
    card.votes += 1
    return CardInfo.model_validate(card)
