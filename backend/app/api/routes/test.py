from fastapi import APIRouter, Depends, Header
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from app.api.dependency.AuthHeaders import AuthHeaders
router = APIRouter(prefix="/test", tags=["test"])


# class HeaderParams:
#     def __init__(
#         self,
#         user_id: Optional[UUID],
#         tenant_id: Optional[UUID],
#         user_type: str,
#         user_designation: Optional[str],
#         user_department: Optional[str],
#         user_is_active: bool,
#     ):
#         self.user_id = user_id
#         self.tenant_id = tenant_id
#         self.user_type = user_type
#         self.user_designation = user_designation
#         self.user_department = user_department
#         self.user_is_active = user_is_active


# def get_header_params(
#     user_id: Optional[str] = Header(None, alias="X-User-ID"),
#     tenant_id: Optional[str] = Header(None, alias="X-Tenant-ID"),
#     user_type: str = Header("employee_access_token", alias="X-User-Type"),
#     user_designation: Optional[str] = Header(None, alias="X-User-Designation"),
#     user_department: Optional[str] = Header(None, alias="X-User-Department"),
#     user_is_active: str = Header("true", alias="X-User-Is-Active"),
# ) -> HeaderParams:
#     # Convert UUIDs if present
#     user_id_val = UUID(user_id) if user_id else None
#     tenant_id_val = UUID(tenant_id) if tenant_id else None
#     user_is_active_val = user_is_active.lower() == "true"

#     return HeaderParams(
#         user_id=user_id_val,
#         tenant_id=tenant_id_val,
#         user_type=user_type,
#         user_designation=user_designation,
#         user_department=user_department,
#         user_is_active=user_is_active_val,
#     )


@router.get("/")
async def health_check(headers: AuthHeaders):
    """Basic health check endpoint"""
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": headers.user_id,
        "tenant_id": headers.tenant_id,
        "user_type": headers.user_type,
        "user_designation": headers.user_designation,
        "user_department": headers.user_department,
        "user_is_active": headers.user_is_active,
    }
