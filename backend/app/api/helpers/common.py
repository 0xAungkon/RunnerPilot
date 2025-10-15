
from fastapi import HTTPException
from app.api.dependency.State import State


def is_tenant_user(state: State) -> bool:
    return state.user.is_tenant_user if state.user else False

def tenant_user_only(state: State):
    if not is_tenant_user(state):
        raise HTTPException(status_code=403, detail="Not enough permissions")

def tenant_permission_check(state: State, tenant_id):
    if not state.user or (state.user.tenant_id != tenant_id and not state.user.is_tenant_user):
        raise HTTPException(status_code=403, detail="Not enough permissions")

def not_found_exception(entity: str = "Item"):
    raise HTTPException(status_code=404, detail=f"{entity} not found")