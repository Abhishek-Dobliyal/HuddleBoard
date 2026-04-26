from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_serializer, model_validator


class ORMBase(BaseModel):
    model_config = {"from_attributes": True}


def _serialize_utc(v: datetime) -> str:
    """Ensure naive UTC datetimes are serialized with timezone suffix."""
    if v.tzinfo is None:
        v = v.replace(tzinfo=timezone.utc)
    return v.isoformat()


class BoardCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field("", max_length=500)
    template: str = Field("retrospective", pattern=r"^(retrospective|4ls|custom)$")
    ttl_hours: int = Field(24, ge=1, le=72)
    password: str | None = Field(None, min_length=4)
    is_readonly_default: bool = False
    custom_columns: list[str] | None = None

    @model_validator(mode="after")
    def validate_custom_columns(self):
        if self.template == "custom":
            if not self.custom_columns:
                raise ValueError("custom_columns required when template is 'custom'")
            if len(self.custom_columns) > 4:
                raise ValueError("Maximum 4 custom columns allowed")
            if any(not col.strip() for col in self.custom_columns):
                raise ValueError("Column names cannot be empty")
            if any(len(col.strip()) > 50 for col in self.custom_columns):
                raise ValueError("Column names must be 50 characters or less")
        return self


class BoardCreated(BaseModel):
    board_id: str
    admin_token: str


class BoardUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=500)
    is_readonly_default: bool | None = None
    password: str | None = Field(None, min_length=4)


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


class CardCreate(BaseModel):
    column_id: str
    text: str = Field(..., min_length=1, max_length=500)
    author_name: str = Field("Anonymous", min_length=1, max_length=30)
    color: str = Field("yellow", pattern=r"^(yellow|pink|blue|green|purple)$")


class CardUpdate(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)


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
