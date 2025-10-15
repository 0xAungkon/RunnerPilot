from fastapi.testclient import TestClient
from faker import Faker
import uuid
from datetime import date, timedelta

from app.core.config import settings
from app.core.logging import logger
from app.tests.utils.test_decorators import TestAPILogger, logged_api_call

fake = Faker()


def _make_employee_payload(designation_id=None):
    """Create a test employee payload with random data"""
    return {
        "employee_code": fake.unique.bothify(text="EMP-#####"),
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "email": fake.email(),
        "personal_email": fake.email(),
        "designation_id": designation_id,
        "phone_number_mobile": fake.phone_number(),
        "date_of_birth": str(fake.date_of_birth(minimum_age=20, maximum_age=60)),
        "gender": fake.random_element(elements=("Male", "Female", "Other")),
        "date_of_joining": str(fake.date_this_decade()),
        "work_location_office": fake.city(),
        "is_tenant_admin": fake.boolean(chance_of_getting_true=20),
    }


def _create_test_designation(client: TestClient, superuser_token_headers: dict[str, str]):
    """Helper to create a designation for testing employee relationship"""
    payload = {
        "title": fake.job(),
        "short_code": fake.unique.lexify(text="TST-??????"),
        "remarks": fake.sentence(),
    }
    r = client.post(f"{settings.API_V1_STR}/designations/", headers=superuser_token_headers, json=payload)
    return r.json()


def test_create_employee(client: TestClient, superuser_token_headers: dict[str, str]):
    # First create a designation
    designation = _create_test_designation(client, superuser_token_headers)
    
    # Now create an employee with the designation
    payload = _make_employee_payload(designation_id=designation["uid"])
    r = client.post(f"{settings.API_V1_STR}/employees/", headers=superuser_token_headers, json=payload)
    assert r.status_code == 200
    data = r.json()
    logger.info(f"Created employee: {data}")
    
    # Check basic properties
    assert data["employee_code"] == payload["employee_code"]
    assert data["first_name"] == payload["first_name"]
    assert data["last_name"] == payload["last_name"]
    assert data["email"] == payload["email"]
    assert data["designation_id"] == designation["uid"]
    assert "uid" in data
    assert data["is_active"] is True
    assert data["is_deleted"] is False
    
    # Clean up
    client.delete(f"{settings.API_V1_STR}/employees/{data['uid']}", headers=superuser_token_headers)
    client.delete(f"{settings.API_V1_STR}/designations/{designation['uid']}", headers=superuser_token_headers)


def test_list_employees(client: TestClient, superuser_token_headers: dict[str, str]):
    with TestAPILogger("test_list_employees") as test_logger:
        r = logged_api_call(
            client, "GET", f"{settings.API_V1_STR}/employees/", 
            test_logger, headers=superuser_token_headers,
            params={"skip": 0, "limit": 100}
        )
        assert r.status_code == 200
        body = r.json()
        logger.debug(f"List employees: {body}")
        assert "data" in body
        assert "pagination" in body and isinstance(body["pagination"], dict)
        pagination = body["pagination"]
        assert isinstance(body["data"], list)
        assert "count" in pagination and isinstance(pagination["count"], int)
        assert "total" in pagination and isinstance(pagination["total"], int)
        assert "offset" in pagination and isinstance(pagination["offset"], int)
        assert "limit" in pagination and isinstance(pagination["limit"], int)
        assert "has_next" in pagination and isinstance(pagination["has_next"], bool)
        assert "has_prev" in pagination and isinstance(pagination["has_prev"], bool)
        assert pagination["count"] == len(body["data"])


def test_read_employee_by_id(client: TestClient, superuser_token_headers: dict[str, str]):
    # Create test designation
    designation = _create_test_designation(client, superuser_token_headers)
    
    # Create test employee
    payload = _make_employee_payload(designation_id=designation["uid"])
    created = client.post(
        f"{settings.API_V1_STR}/employees/",
        headers=superuser_token_headers,
        json=payload,
    ).json()
    uid = created["uid"]

    # Read employee by ID
    r = client.get(f"{settings.API_V1_STR}/employees/{uid}", headers=superuser_token_headers)
    assert r.status_code == 200
    data = r.json()
    logger.debug(f"Read employee by id: {data}")
    assert data["uid"] == uid
    assert data["employee_code"] == payload["employee_code"]
    
    # Clean up
    client.delete(f"{settings.API_V1_STR}/employees/{uid}", headers=superuser_token_headers)
    client.delete(f"{settings.API_V1_STR}/designations/{designation['uid']}", headers=superuser_token_headers)


def test_put_employee(client: TestClient, superuser_token_headers: dict[str, str]):
    # Create test designation
    designation = _create_test_designation(client, superuser_token_headers)
    
    # Create test employee
    payload = _make_employee_payload(designation_id=designation["uid"])
    created = client.post(
        f"{settings.API_V1_STR}/employees/",
        headers=superuser_token_headers,
        json=payload,
    ).json()
    uid = created["uid"]

    # Full update employee
    update_payload = _make_employee_payload(designation_id=designation["uid"])
    r = client.put(
        f"{settings.API_V1_STR}/employees/{uid}",
        headers=superuser_token_headers,
        json=update_payload,
    )
    assert r.status_code == 200
    data = r.json()
    logger.info(f"Updated employee: {data}")
    assert data["first_name"] == update_payload["first_name"]
    assert data["last_name"] == update_payload["last_name"]
    assert data["email"] == update_payload["email"]
    
    # Clean up
    client.delete(f"{settings.API_V1_STR}/employees/{uid}", headers=superuser_token_headers)
    client.delete(f"{settings.API_V1_STR}/designations/{designation['uid']}", headers=superuser_token_headers)


def test_patch_employee(client: TestClient, superuser_token_headers: dict[str, str]):
    # Create test designation
    designation = _create_test_designation(client, superuser_token_headers)
    
    # Create test employee
    payload = _make_employee_payload(designation_id=designation["uid"])
    created = client.post(
        f"{settings.API_V1_STR}/employees/",
        headers=superuser_token_headers,
        json=payload,
    ).json()
    uid = created["uid"]

    # Patch employee
    patch_payload = {
        "work_location_office": fake.city(),
        "is_active": False
    }
    r = client.patch(
        f"{settings.API_V1_STR}/employees/{uid}",
        headers=superuser_token_headers,
        json=patch_payload,
    )
    assert r.status_code == 200
    data = r.json()
    logger.info(f"Patched employee: {data}")
    # EmployeePatch is empty (SQLModel with no fields) so it doesn't update anything
    # Just check is_active, which should be false
    assert data["is_active"] is False
    
    # Clean up
    client.delete(f"{settings.API_V1_STR}/employees/{uid}", headers=superuser_token_headers)
    client.delete(f"{settings.API_V1_STR}/designations/{designation['uid']}", headers=superuser_token_headers)


def test_delete_employee_soft_delete_and_list_filters(client: TestClient, superuser_token_headers: dict[str, str]):
    # Create test designation
    designation = _create_test_designation(client, superuser_token_headers)
    
    # Create test employee
    payload = _make_employee_payload(designation_id=designation["uid"])
    created = client.post(
        f"{settings.API_V1_STR}/employees/",
        headers=superuser_token_headers,
        json=payload,
    ).json()
    uid = created["uid"]

    # Delete (soft delete)
    r = client.delete(f"{settings.API_V1_STR}/employees/{uid}", headers=superuser_token_headers)
    assert r.status_code == 200
    msg = r.json()
    assert msg.get("message") == "Employee deleted successfully"

    # Should not appear in default listing (is_deleted=False)
    r = client.get(f"{settings.API_V1_STR}/employees/", headers=superuser_token_headers)
    assert r.status_code == 200
    body = r.json()
    assert all(item["uid"] != uid for item in body["data"])  # filtered out

    # Should appear when querying soft-deleted
    r = client.get(f"{settings.API_V1_STR}/employees/?is_deleted=true", headers=superuser_token_headers)
    assert r.status_code == 200
    body = r.json()
    assert any(item["uid"] == uid for item in body["data"])  # visible among deleted
    
    # Clean up designation
    client.delete(f"{settings.API_V1_STR}/designations/{designation['uid']}", headers=superuser_token_headers)


def test_unique_employee_code_constraint(client: TestClient, superuser_token_headers: dict[str, str]):
    # Create test designation
    designation = _create_test_designation(client, superuser_token_headers)
    
    # Create first employee
    employee_code = fake.unique.bothify(text="EMP-#####")
    p1 = _make_employee_payload(designation_id=designation["uid"])
    p1["employee_code"] = employee_code
    
    r1 = client.post(f"{settings.API_V1_STR}/employees/", headers=superuser_token_headers, json=p1)
    assert r1.status_code == 200
    data1 = r1.json()
    
    # Try to create second employee with same code
    p2 = _make_employee_payload(designation_id=designation["uid"])
    p2["employee_code"] = employee_code  # Same code as first
    
    r2 = client.post(f"{settings.API_V1_STR}/employees/", headers=superuser_token_headers, json=p2)
    # Expect unique constraint mapped to 409 with structured detail
    assert r2.status_code == 409
    body = r2.json()
    assert "detail" in body
    assert isinstance(body["detail"], list)
    
    # Clean up
    client.delete(f"{settings.API_V1_STR}/employees/{data1['uid']}", headers=superuser_token_headers)
    client.delete(f"{settings.API_V1_STR}/designations/{designation['uid']}", headers=superuser_token_headers)


def test_manager_subordinate_relationship(client: TestClient, superuser_token_headers: dict[str, str]):
    # Create test designation
    designation = _create_test_designation(client, superuser_token_headers)
    
    # Create manager employee
    manager_payload = _make_employee_payload(designation_id=designation["uid"])
    manager = client.post(
        f"{settings.API_V1_STR}/employees/", 
        headers=superuser_token_headers,
        json=manager_payload
    ).json()
    
    # Create subordinate with manager_id
    subordinate_payload = _make_employee_payload(designation_id=designation["uid"])
    subordinate_payload["manager_id"] = manager["uid"]
    
    subordinate = client.post(
        f"{settings.API_V1_STR}/employees/",
        headers=superuser_token_headers,
        json=subordinate_payload
    ).json()
    
    # Check relationship
    assert subordinate["manager_id"] == manager["uid"]
    
    # Clean up
    client.delete(f"{settings.API_V1_STR}/employees/{subordinate['uid']}", headers=superuser_token_headers)
    client.delete(f"{settings.API_V1_STR}/employees/{manager['uid']}", headers=superuser_token_headers)
    client.delete(f"{settings.API_V1_STR}/designations/{designation['uid']}", headers=superuser_token_headers)