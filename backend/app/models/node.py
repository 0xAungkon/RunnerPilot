from enum import Enum
from typing import Optional
import uuid

from sqlmodel import Field, SQLModel

from .common import BaseTable


class NodeType(str, Enum):
    socket = "Socket"
    remote = "Remote"
    local = "Local"


class NodeStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class NodeBase(SQLModel):
    name: str
    ip_address: Optional[str] = None
    port: Optional[int] = None
    socket_path: Optional[str] = None
    type: NodeType
    status: NodeStatus = Field(default=NodeStatus.active)
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    org_id: Optional[uuid.UUID] = Field(default=None, foreign_key="org.uid")


class Node(BaseTable, NodeBase, table=True):
    __tablename__ = "node"


class NodeCreate(NodeBase):
    pass


class NodeUpdate(SQLModel):
    name: Optional[str] = None
    ip_address: Optional[str] = None
    port: Optional[int] = None
    socket_path: Optional[str] = None
    type: Optional[NodeType] = None
    status: Optional[NodeStatus] = None
    user_id: Optional[uuid.UUID] = None
    org_id: Optional[uuid.UUID] = None


class NodePublic(BaseTable, NodeBase):
    pass
