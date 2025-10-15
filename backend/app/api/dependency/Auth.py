from app.api.dependency.AuthJWT import AuthJWT, TokenDep
from app.api.dependency.AuthHeaders import AuthHeaders
from app.api.dependency.State import State
from app.models.common import JWTUserScheme
from typing import Annotated
from fastapi import Depends
from fastapi import HTTPException

def get_current_user(state: State, auth_jwt: AuthJWT, auth_headers: AuthHeaders) -> JWTUserScheme:
    user = getattr(state, "user", None)
    if not user:
        raise HTTPException(status_code=401, detail="Not Authenticated.")
    return user

Auth = Annotated[any, Depends(get_current_user)]
