import uuid
from typing import Any, Literal, List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependency import SessionDep
from app.api.dependency.Auth import get_current_user
from app.crud.designation import DesignationCRUD
from app.models import (
    Designation,
    DesignationCreate,
    DesignationPublic,
    DesignationsPublic,
    DesignationUpdate,
    DesignationPatch,
    Message,
)
from app.api.dependency import State

router = APIRouter(prefix="/designations", dependencies=[Depends(get_current_user)])

designation_crud = DesignationCRUD()
ALLOWED_SEARCH_FIELDS = {"title", "short_code", "remarks"}

@router.get("/", response_model=DesignationsPublic)
async def read_designations(
    state: State,
    session: SessionDep,
    skip: int = Query(0, description="Number of records to skip for pagination"),
    limit: int = Query(100, description="Maximum number of records to return"),
    is_deleted: bool = Query(False, description="Include soft-deleted records when true"),
    search: str | None = Query(None, description="Case-insensitive substring to search for"),
    search_fields: List[Literal["title", "short_code", "remarks"]] | None = Query(
        None,
        description="List of fields to search within; results match if any field contains the term.",
    ),
) -> Any:
    """
    Retrieve designations.
    """
    filters = {}

    filters["tenant_id"] = state.user.tenant_id
    if is_deleted is not None:
        filters['is_deleted'] = is_deleted
    
    # Validate search field against allowlist to avoid applying LIKE on non-text columns
    effective_search = search if search else None
    effective_fields = (
        [f for f in (search_fields or []) if f in ALLOWED_SEARCH_FIELDS] if search else None
    )

    data, pagination = designation_crud.get_multi_with_pagination(
        session=session,
        skip=skip,
        limit=limit,
        search=effective_search,
        search_fields=effective_fields,
        **filters,
    )
    return DesignationsPublic(data=data, pagination=pagination)

@router.get("/{id}", response_model=DesignationPublic)
def read_designation(
    state: State, session: SessionDep, id: uuid.UUID
) -> Any:
    """
    Get designation by ID.
    """
    designation = designation_crud.get_by_id(session=session, obj_id=id)
    if not designation:
        raise HTTPException(status_code=404, detail="Designation not found")
    if not state.user.is_tenant_user and (
        designation.tenant_id != state.user.tenant_id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return designation

@router.post("/", response_model=DesignationPublic)
def create_designation_route(
    state: State,
    session: SessionDep,
    designation_in: DesignationCreate,
) -> Any:
    """
    Create new designation.
    """
    
    return designation_crud.create(session=session, obj_in=designation_in, tenant_id=state.tenant_id)

@router.patch("/{id}", response_model=DesignationPublic)
def patch_designation_route(
    state: State,
    session: SessionDep,
    id: uuid.UUID,
    designation_in: DesignationPatch,
) -> Any:
    """
    Partially update a designation.
    """
    designation = designation_crud.get_by_id(session=session, obj_id=id)
    if not designation:
        raise HTTPException(status_code=404, detail="Designation not found")
    
    if (not getattr(state, "user", None)) or (
        not state.user.is_tenant_user and designation.tenant_id != state.user.tenant_id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    designation = designation_crud.patch(
        session=session, db_obj=designation, obj_in=designation_in
    )
    return designation


@router.put("/{id}", response_model=DesignationPublic)
def update_designation_route(
    state: State,
    session: SessionDep,
    id: uuid.UUID,
    designation_in: DesignationUpdate,
) -> Any:
    """
    Update a designation.
    """
    designation = designation_crud.get_by_id(session=session, obj_id=id)
    if not designation:
        raise HTTPException(status_code=404, detail="Designation not found")
    
    if (not getattr(state, "user", None)) or (
        not state.user.is_tenant_user and designation.tenant_id != state.user.tenant_id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    designation = designation_crud.update(
        session=session, db_obj=designation, obj_in=designation_in
    )
    return designation

@router.delete("/{id}")
def delete_designation_route(
    state: State, session: SessionDep, id: uuid.UUID
) -> Message:
    """
    Delete a designation.
    """
    designation = designation_crud.get_by_id(session=session, obj_id=id)
    if not designation:
        raise HTTPException(status_code=404, detail="Designation not found")
    
    if (not getattr(state, "user", None)) or (
        not state.user.is_tenant_user and designation.tenant_id != state.user.tenant_id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    designation_crud.delete(session=session, db_obj=designation)
    return Message(message="Designation deleted successfully")

