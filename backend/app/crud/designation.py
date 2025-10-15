import uuid
from sqlmodel import Session
from app.models import Designation, DesignationCreate, DesignationUpdate, DesignationPatch
from app.api.dependency import State
from .base import BaseCRUD


class DesignationCRUD(BaseCRUD[Designation, DesignationCreate, DesignationUpdate, DesignationPatch]):
    def __init__(self):
        super().__init__(Designation)