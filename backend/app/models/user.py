from typing import Optional

from pydantic import EmailStr
from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from .common import BaseTable


class UserBase(SQLModel):
    full_name: Optional[str] = None
    email: EmailStr
    password: str


class User(BaseTable, UserBase, table=True):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
    )


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None


class UserPublic(BaseTable, SQLModel):
    full_name: Optional[str] = None
    email: EmailStr
