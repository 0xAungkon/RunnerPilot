#!/usr/bin/env python3
"""
Database Import Script for Employee Service

This script imports sample data from a JSON file into the employee service database.
It handles departments, designations, and employees with proper relationship mapping.

Usage:
    python3 initialdb-loader.py --file /path/to/employee.json --tenant-id YOUR_TENANT_ID
    python3 initialdb-loader.py --default-file --tenant-id YOUR_TENANT_ID  # Uses the default employee.json
"""

import json
import uuid
import argparse
import sys
from datetime import datetime
from pathlib import Path
from sqlmodel import Session, select

# Add the app directory to path so we can import app modules
sys.path.append(str(Path(__file__).parent.parent))

from app.core.db import engine
from app.models.department import Department
from app.models.designation import Designation
from app.models.employee import Employee


def parse_args():
    parser = argparse.ArgumentParser(description="Import data into employee service database")
    parser.add_argument("--file", type=str, help="JSON file containing the data to import", required=False)
    parser.add_argument("--tenant-id", type=str, help="Tenant ID to associate with imported data", required=True)
    parser.add_argument("--from-string", action="store_true", help="Parse JSON from command line")
    parser.add_argument("--default-file", action="store_true", 
                      help="Use the default employee.json file from app/resources/initial-db/")
    return parser.parse_args()


def load_data(file_path=None, from_string=False, use_default=False):
    """Load data from a JSON file or string"""
    if from_string:
        # This option is kept for backward compatibility but should be avoided
        print("Warning: Using hardcoded JSON string is deprecated. Use a file instead.")
        # Simple placeholder JSON structure
        json_data = """{"Departments":[],"Designations":[],"Employees":[]}"""
        return json.loads(json_data)
    elif use_default:
        # Use the default employee.json file from the project
        default_path = Path(__file__).parent.parent / "app" / "resources" / "initial-db" / "employee.json"
        if not default_path.exists():
            raise FileNotFoundError(f"Default file not found at {default_path}")
        print(f"Using default file at: {default_path}")
        with open(default_path, 'r') as f:
            return json.load(f)
    else:
        # Use the specified file path
        with open(file_path, 'r') as f:
            return json.load(f)


def create_designations(session, designations_data, tenant_id):
    """Create designations and return a mapping from old IDs to new UUIDs"""
    print(f"Importing {len(designations_data)} designations...")
    designation_map = {}
    
    for designation in designations_data:
        new_designation = Designation(
            title=designation["Name"],
            short_code=f"DSG-{designation['UID']}",
            remarks=f"Imported from legacy system ID: {designation['UID']}",
            tenant_id=tenant_id,
            is_active=designation["Status"]
        )
        session.add(new_designation)
        session.flush()  # Generate the UUID
        
        designation_map[designation["UID"]] = new_designation.uid
        print(f"Created designation: {new_designation.title} with ID {new_designation.uid}")
    
    return designation_map


def create_departments(session, departments_data, tenant_id):
    """Create departments and return a mapping from old IDs to new UUIDs"""
    print(f"Importing {len(departments_data)} departments...")
    department_map = {}
    
    for department in departments_data:
        new_department = Department(
            name=department["DeptName"],  # Changed from "Name" to "DeptName"
            code=f"DEP-{department['UID']}",
            description=f"Imported from legacy system ID: {department['UID']}",
            tenant_id=tenant_id,
            is_active=department["Status"]
        )
        # We'll handle department head in a second pass after employees are created
        session.add(new_department)
        session.flush()  # Generate the UUID
        
        department_map[department["UID"]] = new_department.uid
        print(f"Created department: {new_department.name} with ID {new_department.uid}")
    
    return department_map


def create_employees(session, employees_data, tenant_id, designation_map, department_map, departments_data):
    """Create employees with proper relationships"""
    print(f"Importing {len(employees_data)} employees...")
    employee_map = {}
    
    # First pass: Create employees without manager relationships
    for employee in employees_data:
        designation_id = designation_map.get(employee["Designation"])
        department_id = department_map.get(employee["Department"])
        
        new_employee = Employee(
            employee_code=employee["EmpID"],
            first_name=employee["FirstName"],
            last_name=employee["LastName"],
            email=employee["WorkEmail"],
            designation_id=designation_id,
            department_id=department_id,  # Set department_id here
            tenant_id=tenant_id,
            is_active=employee["Status"],
        )
        session.add(new_employee)
        session.flush()  # Generate the UUID
        
        employee_map[employee["UID"]] = new_employee.uid
        print(f"Created employee: {new_employee.first_name} {new_employee.last_name} with ID {new_employee.uid}")
    
    # Second pass: Update manager relationships
    for employee in employees_data:
        if employee.get("LineManager"):
            manager_id = employee_map.get(employee["LineManager"])
            if manager_id:
                employee_obj = session.get(Employee, employee_map[employee["UID"]])
                if employee_obj:
                    employee_obj.manager_id = manager_id
                    print(f"Updated employee {employee['FirstName']} with manager ID {manager_id}")
    
    # Third pass: Update department heads
    for department in session.query(Department).all():
        department_uid = next((uid for uid, dept_uid in department_map.items() if dept_uid == department.uid), None)
        if department_uid is not None:
            department_data = next((dept for dept in departments_data if dept["UID"] == department_uid), None)
            if department_data and department_data.get("DeptHead"):
                head_employee_uid = employee_map.get(department_data["DeptHead"])
                if head_employee_uid:
                    department.head_id = head_employee_uid
                    print(f"Updated department {department.name} with head ID {head_employee_uid}")
    
    return employee_map


def import_data(data, tenant_id):
    """Main import function"""
    tenant_uuid = uuid.UUID(tenant_id)
    
    with Session(engine) as session:
        try:
            # Store department data for later reference
            departments_data = data.get("Departments", [])
            designations_data = data.get("Designations", [])
            employees_data = data.get("Employees", [])
            
            print(f"Starting import with {len(departments_data)} departments, {len(designations_data)} designations, and {len(employees_data)} employees")
            
            # Import in order of dependencies
            designation_map = create_designations(session, designations_data, tenant_uuid)
            department_map = create_departments(session, departments_data, tenant_uuid)
            employee_map = create_employees(
                session, 
                employees_data, 
                tenant_uuid,
                designation_map,
                department_map,
                departments_data  # Pass departments_data to handle department heads
            )
            
            session.commit()
            print("Data import completed successfully!")
            
        except Exception as e:
            session.rollback()
            print(f"Error importing data: {e}")
            raise


def main():
    args = parse_args()
    
    if not args.from_string and not args.file and not args.default_file:
        print("Error: Either --file, --default-file, or --from-string must be provided")
        sys.exit(1)
        
    try:
        tenant_id = args.tenant_id
        
        # Validate tenant ID format
        try:
            uuid.UUID(tenant_id)
        except ValueError:
            print(f"Invalid tenant ID format: {tenant_id}. Must be a valid UUID.")
            sys.exit(1)
        
        # Load and import data
        data = load_data(args.file, args.from_string, args.default_file)
        import_data(data, tenant_id)
        
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
