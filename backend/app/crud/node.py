from sqlmodel import Session

from app.models import Node, NodeCreate, NodeUpdate
from .base import BaseCRUD


class NodeCRUD(BaseCRUD[Node, NodeCreate, NodeUpdate, NodeUpdate]):
    def __init__(self):
        super().__init__(Node)
