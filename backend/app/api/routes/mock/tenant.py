import uuid
from typing import Any
import json
from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm

from app import crud
from app.core import security
from app.core.config import settings
from app.core.security import get_password_hash
from app.models import Token
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.dependency import SessionDep , AuthJWT

from app.utils.ExternalAdapters.MockTenentManager import (
    MockTenantManager,
    Tenant as MockTenant,
    Common,
    PlanQuota,
    Usage,
)

router = APIRouter(prefix="/tenants")

mock_tenant_manager = MockTenantManager()


@router.get("/", response_model=dict)
def list_tenants():
    return mock_tenant_manager.list_tenants()


@router.post("/", response_model=str)
def add_tenant(tenant: MockTenant):
    try:
        return mock_tenant_manager.add_tenant(tenant.model_dump())
    except KeyError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{tenant_id}", response_model=dict)
def update_tenant(tenant_id: str, tenant: MockTenant):
    try:
        mock_tenant_manager.update_tenant(tenant_id, tenant.model_dump())
        return {"tenant_id": tenant_id, "updated": True}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{tenant_id}", response_model=dict)
def delete_tenant(tenant_id: str):
    try:
        mock_tenant_manager.delete_tenant(tenant_id)
        return {"tenant_id": tenant_id, "deleted": True}
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{tenant_id}/access-token", response_model=Token)
def tenant_access_token(tenant_id: str):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "identifier": tenant_id,
        "user_type": "tenant_access_token",
        "tenant_id": tenant_id,
    }
    payload = json.dumps(payload)
    return Token(
        access_token=security.create_access_token(
            payload, expires_delta=access_token_expires
        )
    )


@router.post("/{tenant_id}/employee/{employee_id}/access-token", response_model=Token)
def employee_access_token(tenant_id: uuid.UUID, employee_id: uuid.UUID):
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "identifier": str(employee_id),
        "user_type": "employee_access_token",
        "tenant_id": str(tenant_id),
    }
    payload = json.dumps(payload)

    return Token(
        access_token=security.create_access_token(
            payload, expires_delta=access_token_expires
        )
    )

@router.post("/dummy/tenant-token", response_model=Token)
def generate_test_token():
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    tenant_id = uuid.uuid4()
    payload = {
        "identifier": str(tenant_id),
        "user_type": "tenant_access_token",
        "tenant_id": str(tenant_id),
    }
    payload = json.dumps(payload)

    return Token(
        access_token=security.create_access_token(
            payload, expires_delta=access_token_expires
        )
    )

@router.post("/dummy/employee-token", response_model=Token)
def generate_test_token():
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    tenant_id = uuid.uuid4()
    employee_id = uuid.uuid4()
    payload = {
        "identifier": str(employee_id),
        "user_type": "employee_access_token",
        "tenant_id": str(tenant_id),
    }
    payload = json.dumps(payload)

    return Token(
        access_token=security.create_access_token(
            payload, expires_delta=access_token_expires
        )
    )


