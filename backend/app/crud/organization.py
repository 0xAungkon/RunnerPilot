from sqlmodel import Session

from app.models import Org, OrgCreate, OrgUpdate
from .base import BaseCRUD


class OrganizationCRUD(BaseCRUD[Org, OrgCreate, OrgUpdate, OrgUpdate]):
    def __init__(self):
        super().__init__(Org)
