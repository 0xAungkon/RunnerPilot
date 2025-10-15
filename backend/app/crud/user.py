from sqlmodel import Session

from app.models import User, UserCreate, UserUpdate
from .base import BaseCRUD


class UserCRUD(BaseCRUD[User, UserCreate, UserUpdate, UserUpdate]):
    def __init__(self):
        super().__init__(User)
