from enum import Enum
from typing import Optional
import uuid

from sqlmodel import Field, SQLModel

from .common import BaseTable


class RunnerStatus(str, Enum):
    idle = "idle"
    busy = "busy"


class RunnerBase(SQLModel):
    name: str
    status: RunnerStatus = Field(default=RunnerStatus.idle)
    user_id: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    org_id: Optional[uuid.UUID] = Field(default=None, foreign_key="org.uid")
    docker_image: Optional[str] = None
    github_repo: Optional[str] = None
    github_runner_token: Optional[str] = None


class Runner(BaseTable, RunnerBase, table=True):
    __tablename__ = "runners"


class RunnerCreate(RunnerBase):
    pass


class RunnerUpdate(SQLModel):
    name: Optional[str] = None
    status: Optional[RunnerStatus] = None
    user_id: Optional[uuid.UUID] = None
    org_id: Optional[uuid.UUID] = None
    docker_image: Optional[str] = None
    github_repo: Optional[str] = None
    github_runner_token: Optional[str] = None


class RunnerPublic(BaseTable, RunnerBase):
    pass
