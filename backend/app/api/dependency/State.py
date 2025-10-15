from collections.abc import Generator
from typing import Annotated, TypeAlias
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from requests import session
from sqlmodel import Session
from typing import Any, Annotated

from app.core.config import settings
from app.core.db import engine
from fastapi import Request
from fastapi import Security

def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDep: TypeAlias = Annotated[Session, Depends(get_db)]

def get_request_state(request: Request) -> Any:
    
    return request.state

State: TypeAlias = Annotated[Any, Depends(get_request_state)]
