import uuid
from typing import Any, Literal, List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependency import SessionDep
from app.api.dependency.Auth import get_current_user
from app.crud.employee import EmployeeCRUD
from app.models import (
    Employee,
    EmployeeCreate,
    EmployeePublic,
    EmployeesPublic,
    EmployeeUpdate,
    EmployeePatch,
    Message,
)
from app.api.dependency import State

router = APIRouter(prefix="/employees", dependencies=[Depends(get_current_user)])

employee_crud = EmployeeCRUD()
ALLOWED_EMPLOYEE_SEARCH_FIELDS = {
    "employee_code",
    "first_name",
    "last_name",
    "email",
    "personal_email",
    "phone_number_mobile",
    "work_location_office",
    "gender",
}

@router.get("/", response_model=EmployeesPublic)
async def read_employees(
    state: State,
    session: SessionDep,
    skip: int = Query(0, description="Number of records to skip for pagination"),
    limit: int = Query(100, description="Maximum number of records to return"),
    is_deleted: bool = Query(False, description="Include soft-deleted records when true"),
    search: str | None = Query(None, description="Case-insensitive substring to search for"),
    search_fields: List[
        Literal[
            "employee_code",
            "first_name",
            "last_name",
            "email",
            "personal_email",
            "phone_number_mobile",
            "work_location_office",
            "gender",
        ]
    ]
    | None = Query(
        None,
        description="List of fields to search within; results match if any field contains the term.",
    ),
) -> Any:
    """
    Retrieve employees.
    """
    filters = {}

    filters["tenant_id"] = state.user.tenant_id
    if is_deleted is not None:
        filters['is_deleted'] = is_deleted
    
    effective_search = search if search else None
    effective_fields = (
        [f for f in (search_fields or []) if f in ALLOWED_EMPLOYEE_SEARCH_FIELDS] if search else None
    )

    employees, pagination = employee_crud.get_multi_with_pagination(
        session=session,
        skip=skip,
        limit=limit,
        search=effective_search,
        search_fields=effective_fields,
        **filters,
    )
    result = []
    for emp in employees:
        emp_dict = emp.__dict__.copy()
        if emp.designation:
            emp_dict['designation'] = {
                'uid': emp.designation.uid,
                'title': emp.designation.title
            }
        else:
            emp_dict['designation'] = None
        if emp.department:
            emp_dict['department'] = {
                'uid': emp.department.uid,
                'name': emp.department.name
            }
        else:
            emp_dict['department'] = None
        result.append(EmployeePublic(**emp_dict))
    return EmployeesPublic(data=result, pagination=pagination)

@router.get("/{id}", response_model=EmployeePublic)
def read_employee(
    state: State, session: SessionDep, id: uuid.UUID
) -> Any:
    """
    Get employee by ID.
    """
    employee = employee_crud.get_by_id(session=session, obj_id=id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    if not state.user.is_tenant_user and (
        employee.tenant_id != state.user.tenant_id
    ):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    emp_dict = employee.__dict__.copy()
    if employee.designation:
        emp_dict['designation'] = {
            'uid': employee.designation.uid,
            'title': employee.designation.title
        }
    else:
        emp_dict['designation'] = None

    if employee.department:
        emp_dict['department'] = {
            'uid': employee.department.uid,
            'name': employee.department.name
        }
    else:
        emp_dict['department'] = None
    return EmployeePublic(**emp_dict)

@router.post("/", response_model=EmployeePublic)
def create_employee_route(
    state: State,
    session: SessionDep,
    employee_in: EmployeeCreate,
) -> Any:
    """
    Create new employee.
    """
    
    return employee_crud.create(session=session, obj_in=employee_in, tenant_id=state.tenant_id)

@router.patch("/{id}", response_model=EmployeePublic)
def patch_employee_route(
    state: State,
    session: SessionDep,
    id: uuid.UUID,
    employee_in: EmployeePatch,
) -> Any:
    """
    Partially update an employee.
    """
    employee = employee_crud.get_by_id(session=session, obj_id=id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if employee.tenant_id != state.user.tenant_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    employee = employee_crud.patch(
        session=session, db_obj=employee, obj_in=employee_in
    )
    return employee


@router.put("/{id}", response_model=EmployeePublic)
def update_employee_route(
    state: State,
    session: SessionDep,
    id: uuid.UUID,
    employee_in: EmployeeUpdate,
) -> Any:
    """
    Update an employee.
    """
    employee = employee_crud.get_by_id(session=session, obj_id=id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if employee.tenant_id != state.user.tenant_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    employee = employee_crud.update(
        session=session, db_obj=employee, obj_in=employee_in
    )
    return employee

@router.delete("/{id}")
def delete_employee_route(
    state: State, session: SessionDep, id: uuid.UUID
) -> Message:
    """
    Delete an employee.
    """
    employee = employee_crud.get_by_id(session=session, obj_id=id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if employee.tenant_id != state.user.tenant_id:
        raise HTTPException(status_code=400, detail="Not enough permissions")
    
    employee_crud.delete(session=session, db_obj=employee)
    return Message(message="Employee deleted successfully")