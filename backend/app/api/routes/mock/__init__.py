import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import func, select

from app.api.dependency import SessionDep 
from .tenant import router as mock_tenant_router

router = APIRouter(prefix="/mock", tags=["mock"])
router.include_router(mock_tenant_router)