from fastapi import APIRouter
from models import User

router = APIRouter()

@router.post("/")
def create_user(name: str, email: str):
    user = User.create(name=name, email=email)
    return {"id": user.id, "name": user.name, "email": user.email}

@router.get("/")
def list_users():
    return list(User.select().dicts())
