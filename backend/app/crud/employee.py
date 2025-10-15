import uuid
from sqlmodel import Session
from app.models import Employee, EmployeeCreate, EmployeeUpdate, EmployeePatch
from app.api.dependency import State
from .base import BaseCRUD


class EmployeeCRUD(BaseCRUD[Employee, EmployeeCreate, EmployeeUpdate, EmployeePatch]):
    def __init__(self):
        super().__init__(Employee)