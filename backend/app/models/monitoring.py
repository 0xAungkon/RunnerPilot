from datetime import datetime
import uuid

from sqlmodel import Field, SQLModel

from .common import BaseTable


class MonitoringBase(SQLModel):
    runner_instance_id: uuid.UUID = Field(foreign_key="runners_instance.uid")
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Monitoring(BaseTable, MonitoringBase, table=True):
    __tablename__ = "monitoring"


class MonitoringCreate(MonitoringBase):
    pass


class MonitoringPublic(BaseTable, MonitoringBase):
    pass
