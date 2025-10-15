from fastapi.testclient import TestClient
from faker import Faker

from app.core.config import settings
from app.core.logging import logger
from app.tests.utils.test_decorators import TestAPILogger, logged_api_call

fake = Faker()


def _make_department_payload():
    """Create a test department payload with random data"""
    return {
        "name": fake.company(),
        "code": fake.unique.lexify(text="DEPT-??????"),
        "description": fake.text(max_nb_chars=200),
    }


def test_create_department(client: TestClient, superuser_token_headers: dict[str, str]):
    with TestAPILogger("test_create_department") as test_logger:
        payload = _make_department_payload()
        r = logged_api_call(
            client, "POST", f"{settings.API_V1_STR}/departments/", 
            test_logger, headers=superuser_token_headers, json=payload
        )
        assert r.status_code == 200
        data = r.json()
        logger.info(f"Created department: {data}")
        assert data["name"] == payload["name"]
        assert data["code"] == payload["code"]
        assert data["description"] == payload["description"]
        assert "uid" in data and data["uid"]
        assert data["is_active"] is True
        assert data["is_deleted"] is False
        # Clean up
        cleanup_r = logged_api_call(
            client, "DELETE", f"{settings.API_V1_STR}/departments/{data['uid']}", 
            test_logger, headers=superuser_token_headers
        )


def test_list_departments(client: TestClient, superuser_token_headers: dict[str, str]):
    with TestAPILogger("test_list_departments") as test_logger:
        r = logged_api_call(
            client, "GET", f"{settings.API_V1_STR}/departments/", 
            test_logger, headers=superuser_token_headers, 
            params={"skip": 0, "limit": 100}
        )
        assert r.status_code == 200
        body = r.json()
        logger.debug(f"List departments: {body}")
        assert "data" in body and isinstance(body["data"], list)
        assert "pagination" in body and isinstance(body["pagination"], dict)
        pagination = body["pagination"]
        assert "count" in pagination and isinstance(pagination["count"], int)
        assert "total" in pagination and isinstance(pagination["total"], int)
        assert "offset" in pagination and isinstance(pagination["offset"], int)
        assert "limit" in pagination and isinstance(pagination["limit"], int)
        assert "has_next" in pagination and isinstance(pagination["has_next"], bool)
        assert "has_prev" in pagination and isinstance(pagination["has_prev"], bool)
        assert pagination["count"] == len(body["data"])
        assert pagination["count"] >= 0


def test_read_department_by_id(client: TestClient, superuser_token_headers: dict[str, str]):
    with TestAPILogger("test_read_department_by_id") as test_logger:
        payload = _make_department_payload()
        created_r = logged_api_call(
            client, "POST", f"{settings.API_V1_STR}/departments/",
            test_logger, headers=superuser_token_headers, json=payload
        )
        created = created_r.json()
        uid = created["uid"]

        r = logged_api_call(
            client, "GET", f"{settings.API_V1_STR}/departments/{uid}", 
            test_logger, headers=superuser_token_headers
        )
        assert r.status_code == 200
        data = r.json()
        logger.debug(f"Read department by id: {data}")
        assert data["uid"] == uid
        assert data["name"] == payload["name"]
        assert data["code"] == payload["code"]
        # Clean up
        logged_api_call(
            client, "DELETE", f"{settings.API_V1_STR}/departments/{uid}", 
            test_logger, headers=superuser_token_headers
        )


def test_put_department(client: TestClient, superuser_token_headers: dict[str, str]):
    created = client.post(
        f"{settings.API_V1_STR}/departments/",
        headers=superuser_token_headers,
        json=_make_department_payload(),
    ).json()
    uid = created["uid"]

    update_payload = {
        "name": fake.company(),
        "code": fake.unique.lexify(text="UPD-??????"),
        "description": fake.text(max_nb_chars=150),
    }
    r = client.put(
        f"{settings.API_V1_STR}/departments/{uid}",
        headers=superuser_token_headers,
        json=update_payload,
    )
    assert r.status_code == 200
    data = r.json()
    logger.info(f"Updated department: {data}")
    assert data["name"] == update_payload["name"]
    assert data["code"] == update_payload["code"]
    assert data["description"] == update_payload["description"]
    # Clean up
    client.delete(f"{settings.API_V1_STR}/departments/{uid}", headers=superuser_token_headers)


def test_patch_department(client: TestClient, superuser_token_headers: dict[str, str]):
    created = client.post(
        f"{settings.API_V1_STR}/departments/",
        headers=superuser_token_headers,
        json=_make_department_payload(),
    ).json()
    uid = created["uid"]

    patch_payload = {"description": fake.text(max_nb_chars=100), "is_active": False}
    r = client.patch(
        f"{settings.API_V1_STR}/departments/{uid}",
        headers=superuser_token_headers,
        json=patch_payload,
    )
    assert r.status_code == 200
    data = r.json()
    logger.info(f"Patched department: {data}")
    assert data["description"] == patch_payload["description"]
    assert data["is_active"] is False
    # Clean up
    client.delete(f"{settings.API_V1_STR}/departments/{uid}", headers=superuser_token_headers)


def test_delete_department_soft_delete_and_list_filters(client: TestClient, superuser_token_headers: dict[str, str]):
    with TestAPILogger("test_delete_department_soft_delete_and_list_filters") as test_logger:
        created = client.post(
            f"{settings.API_V1_STR}/departments/",
            headers=superuser_token_headers,
            json=_make_department_payload(),
        ).json()
        uid = created["uid"]

        # Delete
        r = logged_api_call(
            client, "DELETE", f"{settings.API_V1_STR}/departments/{uid}", 
            test_logger, headers=superuser_token_headers
        )
        assert r.status_code == 200
        msg = r.json()
        logger.info(f"Delete department response: {msg}")
        assert msg.get("message") == "Department deleted successfully"

        # Should not appear in default listing (is_deleted=False)
        r = logged_api_call(
            client, "GET", f"{settings.API_V1_STR}/departments/", 
            test_logger, headers=superuser_token_headers
        )
        assert r.status_code == 200
        body = r.json()
        logger.debug(f"List after delete: {body}")
        assert all(item["uid"] != uid for item in body["data"])

        # Should appear when querying soft-deleted
        r = logged_api_call(
            client, "GET", f"{settings.API_V1_STR}/departments/?is_deleted=true", 
            test_logger, headers=superuser_token_headers
        )
        assert r.status_code == 200
        body = r.json()
        logger.debug(f"List soft-deleted: {body}")
        assert any(item["uid"] == uid for item in body["data"])


def test_unique_department_code_conflict(client: TestClient, superuser_token_headers: dict[str, str]):
    code = fake.unique.lexify(text="DEPT-??????")
    p1 = {"name": fake.company(), "code": code, "description": fake.sentence(nb_words=3)}
    p2 = {"name": fake.company(), "code": code, "description": fake.sentence(nb_words=3)}

    r1 = client.post(f"{settings.API_V1_STR}/departments/", headers=superuser_token_headers, json=p1)
    assert r1.status_code == 200
    data1 = r1.json()
    logger.debug(f"First department for unique test: {data1}")

    r2 = client.post(f"{settings.API_V1_STR}/departments/", headers=superuser_token_headers, json=p2)
    logger.info(f"Second department (should conflict): {r2.json()}")
    assert r2.status_code == 409
    body = r2.json()
    assert "detail" in body
    assert isinstance(body["detail"], list)
    # Clean up
    client.delete(f"{settings.API_V1_STR}/departments/{data1['uid']}", headers=superuser_token_headers)
