import uuid
from typing import Any, Literal, List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependency import SessionDep
from app.api.dependency.Auth import get_current_user
from app.crud.department import DepartmentCRUD
from app.models import (
    Department,
    DepartmentCreate,
    DepartmentPublic,
    DepartmentsPublic,
    DepartmentUpdate,
    DepartmentPatch,
    Message,
)
from app.api.dependency import State
from app.crud.employee import EmployeeCRUD


router = APIRouter(prefix="/departments", dependencies=[Depends(get_current_user)])

department_crud = DepartmentCRUD()


@router.get("/", response_model=DepartmentsPublic)
def read_departments(
    state: State,
    session: SessionDep,
    skip: int = Query(0, description="Number of records to skip for pagination"),
    limit: int = Query(100, description="Maximum number of records to return"),
    is_deleted: bool = Query(False, description="Include soft-deleted records when true"),
    search: str | None = Query(None, description="Case-insensitive substring to search for"),
    search_fields: List[Literal["name", "code", "description"]] | None = Query(
        None, description="List of fields to search within; results match if any field contains the term."
    ),
) -> Any:
    """Retrieve departments scoped by tenant with optional search."""
    filters: dict[str, Any] = {"tenant_id": state.user.tenant_id}
    if is_deleted is not None:
        filters["is_deleted"] = is_deleted
    departments, pagination = department_crud.get_multi_with_pagination(
        session=session,
        skip=skip,
        limit=limit,
        search=search,
        search_fields=search_fields,
        **filters,
    )
    employee_crud = EmployeeCRUD()
    enriched_departments = []
    for dept in departments:
        head_info = None
        if dept.head_id:
            head = employee_crud.get_by_id(session=session, obj_id=dept.head_id)
            if head:
                head_info = {
                    "uid": head.uid,
                    "name": f"{head.first_name or ''} {head.last_name or ''}".strip(),
                    "email": head.email,
                }
        dept_public = DepartmentPublic(**dept.model_dump(), head=head_info)
        enriched_departments.append(dept_public)
    return DepartmentsPublic(data=enriched_departments, pagination=pagination)


@router.get("/{id}", response_model=DepartmentPublic)
def read_department(state: State, session: SessionDep, id: uuid.UUID) -> Any:
    """Get department by ID with cross-tenant check."""
    department = department_crud.get_by_id(session=session, obj_id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    if not state.user.is_tenant_user and (department.tenant_id != state.user.tenant_id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    from app.crud.employee import EmployeeCRUD
    employee_crud = EmployeeCRUD()
    head_info = None
    if department.head_id:
        head = employee_crud.get_by_id(session=session, obj_id=department.head_id)
        if head:
            head_info = {
                "uid": head.uid,
                "name": f"{head.first_name or ''} {head.last_name or ''}".strip(),
                "email": head.email,
            }
    return DepartmentPublic(**department.model_dump(), head=head_info)


@router.post("/", response_model=DepartmentPublic)
def create_department_route(
    state: State, session: SessionDep, department_in: DepartmentCreate
) -> Any:
    """Create new department; tenant_id is injected from request state."""
    return department_crud.create(session=session, obj_in=department_in, tenant_id=state.tenant_id)


@router.patch("/{id}", response_model=DepartmentPublic)
def patch_department_route(
    state: State, session: SessionDep, id: uuid.UUID, department_in: DepartmentPatch
) -> Any:
    """Partially update a department after tenant check."""
    department = department_crud.get_by_id(session=session, obj_id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    if department.tenant_id != state.user.tenant_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return department_crud.patch(session=session, db_obj=department, obj_in=department_in)


@router.put("/{id}", response_model=DepartmentPublic)
def update_department_route(
    state: State, session: SessionDep, id: uuid.UUID, department_in: DepartmentUpdate
) -> Any:
    """Update a department after tenant check."""
    department = department_crud.get_by_id(session=session, obj_id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    if department.tenant_id != state.user.tenant_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return department_crud.update(session=session, db_obj=department, obj_in=department_in)


@router.delete("/{id}")
def delete_department_route(state: State, session: SessionDep, id: uuid.UUID) -> Message:
    """Soft delete a department after tenant check."""
    department = department_crud.get_by_id(session=session, obj_id=id)
    if not department:
        raise HTTPException(status_code=404, detail="Department not found")
    if department.tenant_id != state.user.tenant_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    department_crud.delete(session=session, db_obj=department)
    return Message(message="Department deleted successfully")
