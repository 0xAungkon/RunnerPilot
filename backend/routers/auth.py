from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from inc.config import settings
from inc.auth import create_access_token
from datetime import timedelta

router = APIRouter()


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def login(req: LoginRequest):
    # naive static auth against settings
    if req.email != settings.ADMIN_EMAIL or req.password != settings.ADMIN_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": req.email})
    return {"access_token": token, "token_type": "bearer"}
