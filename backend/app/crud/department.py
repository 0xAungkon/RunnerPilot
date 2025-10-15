import uuid
from sqlmodel import Session
from app.models import Department, DepartmentCreate, DepartmentUpdate, DepartmentPatch
from .base import BaseCRUD


class DepartmentCRUD(BaseCRUD[Department, DepartmentCreate, DepartmentUpdate, DepartmentPatch]):
    def __init__(self):
        super().__init__(Department)
