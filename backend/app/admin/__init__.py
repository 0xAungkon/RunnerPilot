from app.admin.views import EmployeeAdmin, DepartmentAdmin, DesignationAdmin
from app.admin.setup import setup_admin

# Import other admin views as needed

__all__ = [
    "EmployeeAdmin",
    "DepartmentAdmin", 
    "DesignationAdmin",
    "setup_admin"
]