from fastapi import APIRouter, Depends
from inc.auth import authorized_user, AuthorizedUser

router = APIRouter()


@router.get("/me", response_model=AuthorizedUser)
def me(user: AuthorizedUser = Depends(authorized_user)):
    return user
