from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_serializer, model_validator
from app.constants import (
    TITLE_MAX_LENGTH, DESCRIPTION_MAX_LENGTH, CARD_TEXT_MAX_LENGTH,
    COLUMN_NAME_MAX_LENGTH, AUTHOR_NAME_MAX_LENGTH, PASSWORD_MIN_LENGTH,
    DEFAULT_TTL_HOURS, TTL_MIN_HOURS, TTL_MAX_HOURS,
    DEFAULT_TEMPLATE, DEFAULT_AUTHOR, DEFAULT_CARD_COLOR,
    MAX_CUSTOM_COLUMNS, VALID_CARD_COLORS,
)


class ORMBase(BaseModel):
    model_config = {"from_attributes": True}


def _serialize_utc(v: datetime) -> str:
    """Ensure naive UTC datetimes are serialized with timezone suffix."""
    if v.tzinfo is None:
        v = v.replace(tzinfo=timezone.utc)
    return v.isoformat()


class BoardCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=TITLE_MAX_LENGTH)
    description: str = Field("", max_length=DESCRIPTION_MAX_LENGTH)
    template: str = Field(DEFAULT_TEMPLATE, pattern=r"^(retrospective|4ls|custom)$")
    ttl_hours: int = Field(DEFAULT_TTL_HOURS, ge=TTL_MIN_HOURS, le=TTL_MAX_HOURS)
    password: str | None = Field(None, min_length=PASSWORD_MIN_LENGTH)
    is_readonly_default: bool = False
    custom_columns: list[str] | None = None

    @model_validator(mode="after")
    def validate_custom_columns(self):
        if self.template == "custom":
            if not self.custom_columns:
                raise ValueError("custom_columns required when template is 'custom'")
            if len(self.custom_columns) > MAX_CUSTOM_COLUMNS:
                raise ValueError(f"Maximum {MAX_CUSTOM_COLUMNS} custom columns allowed")
            if any(not col.strip() for col in self.custom_columns):
                raise ValueError("Column names cannot be empty")
            if any(len(col.strip()) > COLUMN_NAME_MAX_LENGTH for col in self.custom_columns):
                raise ValueError(f"Column names must be {COLUMN_NAME_MAX_LENGTH} characters or less")
        return self


class BoardCreated(BaseModel):
    board_id: str
    admin_token: str


class BoardUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=TITLE_MAX_LENGTH)
    description: str | None = Field(None, max_length=DESCRIPTION_MAX_LENGTH)
    is_readonly_default: bool | None = None
    password: str | None = Field(None, min_length=PASSWORD_MIN_LENGTH)


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

    @field_serializer("expires_at", "created_at")
    def serialize_dt(self, v: datetime, _info) -> str:
        return _serialize_utc(v)

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


_color_pattern = "^(" + "|".join(VALID_CARD_COLORS) + ")$"

class CardCreate(BaseModel):
    column_id: str
    text: str = Field(..., min_length=1, max_length=CARD_TEXT_MAX_LENGTH)
    author_name: str = Field(DEFAULT_AUTHOR, min_length=1, max_length=AUTHOR_NAME_MAX_LENGTH)
    color: str = Field(DEFAULT_CARD_COLOR, pattern=_color_pattern)


class CardUpdate(BaseModel):
    text: str = Field(..., min_length=1, max_length=CARD_TEXT_MAX_LENGTH)


class CardMove(BaseModel):
    column_id: str


class CardInfo(ORMBase):
    id: str
    column_id: str
    text: str
    author_name: str
    votes: int
    color: str
    created_at: datetime

    @field_serializer("created_at")
    def serialize_dt(self, v: datetime, _info) -> str:
        return _serialize_utc(v)


class BoardFull(BaseModel):
    board: BoardInfo
    columns: list[ColumnInfo]
    cards: list[CardInfo]
