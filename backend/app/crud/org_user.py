from sqlmodel import Session

from app.models import OrgUser, OrgUserCreate, OrgUserUpdate
from .base import BaseCRUD


class OrgUserCRUD(BaseCRUD[OrgUser, OrgUserCreate, OrgUserUpdate, OrgUserUpdate]):
    def __init__(self):
        super().__init__(OrgUser)
