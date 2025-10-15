from sqlmodel import Session

from app.models import RunnerInstance, RunnerInstanceCreate, RunnerInstanceUpdate
from .base import BaseCRUD


class RunnerInstanceCRUD(BaseCRUD[RunnerInstance, RunnerInstanceCreate, RunnerInstanceUpdate, RunnerInstanceUpdate]):
    def __init__(self):
        super().__init__(RunnerInstance)
