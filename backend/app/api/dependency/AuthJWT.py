from collections.abc import Generator
from typing import Annotated
import json
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session
from typing import Any, Annotated

from app.core import security
from app.core.config import settings
from app.core.db import engine
from app.models import JWTUserScheme
from fastapi import Request
from fastapi import Security

bearer_scheme = HTTPBearer(auto_error=False)
TokenDep = Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]


def get_barrier_token(request: Request, credentials: TokenDep) -> Any:
    return None

AuthJWT = Annotated[JWTUserScheme, Depends(get_barrier_token)]


