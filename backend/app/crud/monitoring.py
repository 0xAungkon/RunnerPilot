from sqlmodel import Session

from app.models import Monitoring, MonitoringCreate
from .base import BaseCRUD


class MonitoringCRUD(BaseCRUD[Monitoring, MonitoringCreate, MonitoringCreate, MonitoringCreate]):
    def __init__(self):
        super().__init__(Monitoring)
