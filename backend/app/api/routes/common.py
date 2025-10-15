from datetime import timedelta
from typing import Annotated, Any

from app.api.dependency.Auth import get_current_user
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.api.dependency import State
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash

router = APIRouter(tags=["common"], dependencies=[Depends(get_current_user)])

@router.get("/common/me")
def me(state: State) -> Any:
    """
    Test access token
    """

    return state.user
    

