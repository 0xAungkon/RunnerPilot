import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel
from enum import Enum

# Generic message
class Message(SQLModel):
    message: str


# Pagination model for list responses
class Pagination(SQLModel):
    total: int
    offset: int
    limit: int
    count: int
    has_next: bool
    has_prev: bool


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None


# Base mixin for DB tables with common fields
class BaseTable(SQLModel):
    uid: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"onupdate": datetime.utcnow},
    )
    deleted_at: datetime | None = None
    is_deleted: bool = Field(default=False)
    is_active: bool = Field(default=True)




class JWTUserScheme(SQLModel):
    identifier: uuid.UUID
    is_active: bool = True