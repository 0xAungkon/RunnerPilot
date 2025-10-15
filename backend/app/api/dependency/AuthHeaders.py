from fastapi import Depends, Header
from typing import Optional
from uuid import UUID
from typing import Annotated

class HeaderParams:
    def __init__(
        self,
        user_id: Optional[UUID],
        tenant_id: Optional[UUID],
        user_type: str,
        user_designation: Optional[str],
        user_department: Optional[str],
        user_is_active: bool,
    ):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.user_type = user_type
        self.user_designation = user_designation
        self.user_department = user_department
        self.user_is_active = user_is_active

def get_header_params(
    user_id: Optional[str] = Header(None, alias="X-User-ID", include_in_schema=False),
    tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID", include_in_schema=False),
    user_type: str = Header("employee_access_token", alias="X-User-Type", include_in_schema=False),
    user_designation: Optional[str] = Header(None, alias="X-User-Designation", include_in_schema=False),
    user_department: Optional[str] = Header(None, alias="X-User-Department", include_in_schema=False),
    user_is_active: str = Header("true", alias="X-User-Is-Active", include_in_schema=False),
) -> HeaderParams:
    user_id_val = UUID(user_id) if user_id else None
    tenant_id_val = UUID(tenant_id) if tenant_id else None
    user_is_active_val = user_is_active.lower() == "true"
    return HeaderParams(
        user_id=user_id_val,
        tenant_id=tenant_id_val,
        user_type=user_type,
        user_designation=user_designation,
        user_department=user_department,
        user_is_active=user_is_active_val,
    )

AuthHeaders = Annotated[HeaderParams, Depends(get_header_params)]
