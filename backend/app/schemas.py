from datetime import datetime
from pydantic import BaseModel, Field


class ORMBase(BaseModel):
    model_config = {"from_attributes": True}


class BoardCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field("", max_length=500)
    template: str = Field("retrospective", pattern=r"^(retrospective|4ls|custom)$")
    ttl_hours: int = Field(24, ge=1, le=72)
    password: str | None = None
    is_readonly_default: bool = False
    custom_columns: list[str] | None = None  # required when template == "custom"


class BoardCreated(BaseModel):
    board_id: str
    admin_token: str


class BoardUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    is_readonly_default: bool | None = None
    password: str | None = None  # set new password, or null to remove


class BoardInfo(ORMBase):
    id: str
    title: str
    description: str
    template: str
    ttl_hours: int
    expires_at: datetime
    has_password: bool
    is_readonly_default: bool
    created_at: datetime

    @classmethod
    def from_board(cls, board) -> "BoardInfo":
        return cls(
            id=board.id,
            title=board.title,
            description=board.description,
            template=board.template,
            ttl_hours=board.ttl_hours,
            expires_at=board.expires_at,
            has_password=board.password_hash is not None,
            is_readonly_default=board.is_readonly_default,
            created_at=board.created_at,
        )


class ColumnInfo(ORMBase):
    id: str
    board_id: str
    title: str
    color: str
    position: int


class CardCreate(BaseModel):
    column_id: str
    text: str = Field(..., min_length=1, max_length=500)
    author_name: str = Field("Anonymous", min_length=1, max_length=30)
    color: str = Field("yellow", pattern=r"^(yellow|pink|blue|green|purple)$")


class CardUpdate(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


class CardInfo(ORMBase):
    id: str
    column_id: str
    text: str
    author_name: str
    votes: int
    color: str
    created_at: datetime


class BoardFull(BaseModel):
    board: BoardInfo
    columns: list[ColumnInfo]
    cards: list[CardInfo]
