from enum import Enum
from typing import Optional
import uuid

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from .common import BaseTable


class OrgType(str, Enum):
    personal = "personal"
    organization = "organization"


class OrgBase(SQLModel):
    name: str
    org_type: OrgType = Field(default=OrgType.organization)
    org_creator: uuid.UUID = Field(foreign_key="users.uid")


class Org(BaseTable, OrgBase, table=True):
    __tablename__ = "org"
    __table_args__ = (
        UniqueConstraint("name", name="uq_org_name"),
    )


class OrgCreate(OrgBase):
    pass


class OrgUpdate(SQLModel):
    name: Optional[str] = None
    org_type: Optional[OrgType] = None
    org_creator: Optional[str] = None


class OrgPublic(BaseTable, OrgBase):
    pass
