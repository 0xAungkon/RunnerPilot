from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import jwt
from inc.config import settings
from pydantic import BaseModel, EmailStr
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    return payload


class AuthorizedUser(BaseModel):
    sub: EmailStr
    exp: datetime


_bearer_scheme = HTTPBearer(auto_error=True)

def authorized_user():
    pass

# def authorized_user(credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme)) -> AuthorizedUser:
#     token = credentials.credentials
#     try:
#         payload = decode_access_token(token)
#         # Normalize exp to datetime if necessary
#         exp_value = payload.get("exp")
#         if isinstance(exp_value, (int, float)):
#             exp_dt = datetime.utcfromtimestamp(int(exp_value))
#         elif isinstance(exp_value, str):
#             # best-effort parse ISO; fall back to error
#             try:
#                 exp_dt = datetime.fromisoformat(exp_value)
#             except Exception as _:
#                 raise HTTPException(status_code=401, detail="Invalid token expiration format")
#         elif isinstance(exp_value, datetime):
#             exp_dt = exp_value
#         else:
#             raise HTTPException(status_code=401, detail="Missing token expiration")

#         sub = payload.get("sub")
#         if not sub:
#             raise HTTPException(status_code=401, detail="Missing subject in token")

#         return AuthorizedUser(sub=sub, exp=exp_dt)
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=401, detail=str(e))
