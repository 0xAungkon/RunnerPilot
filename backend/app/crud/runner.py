from sqlmodel import Session

from app.models import Runner, RunnerCreate, RunnerUpdate
from .base import BaseCRUD


class RunnerCRUD(BaseCRUD[Runner, RunnerCreate, RunnerUpdate, RunnerUpdate]):
    def __init__(self):
        super().__init__(Runner)
