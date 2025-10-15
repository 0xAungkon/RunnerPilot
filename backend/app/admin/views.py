from sqladmin import ModelView
from app.models.department import Department
from app.models.designation import Designation
from app.models.employee import Employee


class EmployeeAdmin(ModelView, model=Employee):
    name = "Employee"
    name_plural = "Employees"
    icon = "fa-solid fa-users"
    column_list = [
        Employee.uid,
        Employee.employee_code, 
        Employee.first_name, 
        Employee.last_name, 
        Employee.email,
        Employee.tenant_id,
        Employee.designation_id,
        Employee.is_active
    ]
    column_searchable_list = [
        Employee.employee_code,
        Employee.first_name,
        Employee.last_name,
        Employee.email
    ]
    column_sortable_list = [
        Employee.employee_code,
        Employee.first_name,
        Employee.last_name,
        Employee.is_active,
    ]
    column_details_exclude_list = [Employee.deleted_at]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class DepartmentAdmin(ModelView, model=Department):
    name = "Department"
    name_plural = "Departments"
    icon = "fa-solid fa-building"
    column_list = [
        Department.uid,
        Department.tenant_id,
        Department.name,
        Department.code,
        Department.description,
        Department.is_active
    ]
    column_searchable_list = [Department.name, Department.code]
    column_sortable_list = [Department.name, Department.is_active]
    column_details_exclude_list = [Department.deleted_at]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True


class DesignationAdmin(ModelView, model=Designation):
    name = "Designation"
    name_plural = "Designations"
    icon = "fa-solid fa-id-badge"
    column_list = [
        Designation.uid,
        Designation.tenant_id,
        Designation.title,
        Designation.short_code,
        Designation.remarks,
        Designation.is_active
    ]
    column_searchable_list = [Designation.title, Designation.short_code]
    column_sortable_list = [Designation.title, Designation.is_active]
    column_details_exclude_list = [Designation.deleted_at]
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True