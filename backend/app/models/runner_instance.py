from enum import Enum
from typing import Optional
import uuid
from datetime import datetime

from sqlmodel import Field, JSON, SQLModel

from .common import BaseTable


class RunnerInstanceStatus(str, Enum):
    online = "online"
    offline = "offline"
    busy = "busy"
    idle = "idle"


class RunnerInstanceBase(SQLModel):
    runner_id: uuid.UUID = Field(foreign_key="runners.uid")
    node_id: uuid.UUID = Field(foreign_key="node.uid")
    instance_identifier: Optional[str] = None
    instance_host: Optional[str] = None
    instance_meta: Optional[dict] = Field(default=None, sa_column=JSON)
    status: RunnerInstanceStatus = Field(default=RunnerInstanceStatus.offline)
    last_heartbeat: Optional[datetime] = None


class RunnerInstance(BaseTable, RunnerInstanceBase, table=True):
    __tablename__ = "runners_instance"


class RunnerInstanceCreate(RunnerInstanceBase):
    pass


class RunnerInstanceUpdate(SQLModel):
    instance_identifier: Optional[str] = None
    instance_host: Optional[str] = None
    instance_meta: Optional[dict] = None
    status: Optional[RunnerInstanceStatus] = None
    last_heartbeat: Optional[str] = None


class RunnerInstancePublic(BaseTable, RunnerInstanceBase):
    pass
