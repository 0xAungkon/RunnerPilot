from fastapi import APIRouter, Header, HTTPException
from typing import Optional
from inc.auth import decode_access_token

router = APIRouter()


@router.get("/me")
def me(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = parts[1]
    try:
        payload = decode_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

    return {"token": payload}
