from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from jwt.exceptions import InvalidTokenError
import json
from app.core import security
from app.core.config import settings
from app.models import TokenPayload, JWTUserScheme
import jwt
import uuid
from loguru import logger 

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        if getattr(request.state, "user", None) is not None:
            return await call_next(request)
        # Check for the presence of the Authorization header

        token = request.headers.get("Authorization")
        if token:
            if token.startswith("Bearer "):
                token = token.split(" ")[1]
            
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[security.ALGORITHM])
                token_data = TokenPayload(**payload)
                sub_payload = json.loads(token_data.sub)
                user = JWTUserScheme(**sub_payload)
                request.state.tenant_id = user.tenant_id
                request.state.user = user
                request.state.is_tenant_user = user.is_tenant_user
            except (InvalidTokenError, json.JSONDecodeError, ValueError):
                request.state.user = None
                logger.warning("Invalid token or unable to decode user information.")

        response = await call_next(request)
        
        return response
    
# Middleware to extract user info from custom headers for local development
class HeadersAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if getattr(request.state, "user", None) is not None:
            return await call_next(request)
        # Check for the presence of the Authorization header

        if settings.ENVIRONMENT != "local":
            return await call_next(request)
        
        user_id = request.headers.get("X-User-ID")
        tenant_id = request.headers.get("X-Tenant-ID")
        user_type = request.headers.get("X-User-Type", "employee_access_token")
        user_designation = request.headers.get("X-User-Designation")
        user_department = request.headers.get("X-User-Department")
        user_is_active = request.headers.get("X-User-Is-Active", "true").lower() == "true"
        if user_id and tenant_id:
            try:
                user = JWTUserScheme(
                    user_type=user_type,
                    tenant_id=uuid.UUID(tenant_id),
                    identifier=uuid.UUID(user_id),
                    designation=uuid.UUID(user_designation) if user_designation else None,
                    department=uuid.UUID(user_department) if user_department else None,
                    is_active=user_is_active
                )

                request.state.tenant_id = user.tenant_id
                request.state.user = user
                request.state.is_tenant_user = user.is_tenant_user
            except ValueError:
                request.state.user = None
                logger.warning("Invalid UUID format in headers.")

        response = await call_next(request)
        
        return response