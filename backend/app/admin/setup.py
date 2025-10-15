"""
SQLAdmin setup module for Employee Service
"""
from fastapi import FastAPI
from sqladmin import Admin
from app.core.db import engine
from app.core.config import settings
from app.admin.views import EmployeeAdmin, DepartmentAdmin, DesignationAdmin

def setup_admin(app: FastAPI):
    """
    Initialize and configure SQLAdmin for the application
    
    Args:
        app: FastAPI application instance
    
    Returns:
        The configured Admin instance
    """
    if not settings.IS_DEV:
        # In production, you might want to use proper auth
        from app.admin.auth import AdminAuth
        authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
    else:
        # For development, no auth
        authentication_backend = None
    
    # Initialize SQLAdmin
    admin = Admin(
        app,
        engine,
        title="Employee Service Admin",
        authentication_backend=authentication_backend
    )

    # Register admin views
    admin.add_view(EmployeeAdmin)
    admin.add_view(DepartmentAdmin)
    admin.add_view(DesignationAdmin)
    
    return admin