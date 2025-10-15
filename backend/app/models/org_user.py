from enum import Enum
from typing import Optional
import uuid

from sqlmodel import Field, JSON, SQLModel

from .common import BaseTable


class OrgUserRole(str, Enum):
    admin = "admin"
    member = "member"


class OrgUserBase(SQLModel):
    org_id: uuid.UUID = Field(foreign_key="org.uid")
    user_id: uuid.UUID = Field(foreign_key="users.uid")
    role: OrgUserRole = Field(default=OrgUserRole.member)
    permissions: Optional[dict] = Field(default=None, sa_column=JSON)


class OrgUser(BaseTable, OrgUserBase, table=True):
    __tablename__ = "org_users"


class OrgUserCreate(OrgUserBase):
    pass


class OrgUserUpdate(SQLModel):
    role: Optional[OrgUserRole] = None
    permissions: Optional[dict] = None


class OrgUserPublic(BaseTable, OrgUserBase):
    pass
