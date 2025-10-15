from fastapi.testclient import TestClient
from faker import Faker

from app.core.config import settings
from app.core.logging import logger
from app.tests.utils.test_decorators import TestAPILogger, logged_api_call

fake = Faker()


def _make_designation_payload():
    return {
        "title": fake.job(),
        "short_code": fake.unique.lexify(text="SC-??????"),
        "remarks": fake.sentence(nb_words=6),
    }


def test_create_designation(client: TestClient, superuser_token_headers: dict[str, str]):
    with TestAPILogger("test_create_designation") as test_logger:
        payload = _make_designation_payload()
        r = logged_api_call(
            client, "POST", f"{settings.API_V1_STR}/designations/", 
            test_logger, headers=superuser_token_headers, json=payload
        )
        assert r.status_code == 200
        data = r.json()
        logger.info(f"Created designation: {data}")
        assert data["title"] == payload["title"]
        assert data["short_code"] == payload["short_code"]
        assert data["remarks"] == payload["remarks"]
        assert "uid" in data and data["uid"]
        assert data["is_active"] is True
        assert data["is_deleted"] is False
        # Clean up
        cleanup_r = logged_api_call(
            client, "DELETE", f"{settings.API_V1_STR}/designations/{data['uid']}", 
            test_logger, headers=superuser_token_headers
        )


def test_list_designations(client: TestClient, superuser_token_headers: dict[str, str]):
    with TestAPILogger("test_list_designations") as test_logger:
        r = logged_api_call(
            client, "GET", f"{settings.API_V1_STR}/designations/", 
            test_logger, headers=superuser_token_headers, 
            params={"skip": 0, "limit": 100}
        )
        assert r.status_code == 200
        body = r.json()
        logger.debug(f"List designations: {body}")
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
        assert pagination["count"] >= 0  # could be zero if cleaned up


def test_read_designation_by_id(client: TestClient, superuser_token_headers: dict[str, str]):
    with TestAPILogger("test_read_designation_by_id") as test_logger:
        payload = _make_designation_payload()
        created_r = logged_api_call(
            client, "POST", f"{settings.API_V1_STR}/designations/",
            test_logger, headers=superuser_token_headers, json=payload
        )
        created = created_r.json()
        uid = created["uid"]

        r = logged_api_call(
            client, "GET", f"{settings.API_V1_STR}/designations/{uid}", 
            test_logger, headers=superuser_token_headers
        )
        assert r.status_code == 200
        data = r.json()
        logger.debug(f"Read designation by id: {data}")
        assert data["uid"] == uid
        # Clean up
        logged_api_call(
            client, "DELETE", f"{settings.API_V1_STR}/designations/{uid}", 
            test_logger, headers=superuser_token_headers
        )


def test_put_designation(client: TestClient, superuser_token_headers: dict[str, str]):
    created = client.post(
        f"{settings.API_V1_STR}/designations/",
        headers=superuser_token_headers,
        json=_make_designation_payload(),
    ).json()
    uid = created["uid"]

    update_payload = {
        "title": fake.job(),
        "short_code": fake.unique.lexify(text="UP-??????"),
        "remarks": fake.sentence(nb_words=5),
    }
    r = client.put(
        f"{settings.API_V1_STR}/designations/{uid}",
        headers=superuser_token_headers,
        json=update_payload,
    )
    assert r.status_code == 200
    data = r.json()
    logger.info(f"Updated designation: {data}")
    assert data["title"] == update_payload["title"]
    assert data["short_code"] == update_payload["short_code"]
    assert data["remarks"] == update_payload["remarks"]
    # Clean up
    client.delete(f"{settings.API_V1_STR}/designations/{uid}", headers=superuser_token_headers)


def test_patch_designation(client: TestClient, superuser_token_headers: dict[str, str]):
    created = client.post(
        f"{settings.API_V1_STR}/designations/",
        headers=superuser_token_headers,
        json=_make_designation_payload(),
    ).json()
    uid = created["uid"]

    patch_payload = {"remarks": fake.sentence(nb_words=4), "is_active": False}
    r = client.patch(
        f"{settings.API_V1_STR}/designations/{uid}",
        headers=superuser_token_headers,
        json=patch_payload,
    )
    assert r.status_code == 200
    data = r.json()
    logger.info(f"Patched designation: {data}")
    assert data["remarks"] == patch_payload["remarks"]
    assert data["is_active"] is False
    # Clean up
    client.delete(f"{settings.API_V1_STR}/designations/{uid}", headers=superuser_token_headers)


def test_delete_designation_soft_delete_and_list_filters(client: TestClient, superuser_token_headers: dict[str, str]):
    created = client.post(
        f"{settings.API_V1_STR}/designations/",
        headers=superuser_token_headers,
        json=_make_designation_payload(),
    ).json()
    uid = created["uid"]

    # Delete
    r = client.delete(f"{settings.API_V1_STR}/designations/{uid}", headers=superuser_token_headers)
    assert r.status_code == 200
    msg = r.json()
    logger.info(f"Delete designation response: {msg}")
    assert msg.get("message") == "Designation deleted successfully"

    # Should not appear in default listing (is_deleted=False)
    r = client.get(f"{settings.API_V1_STR}/designations/", headers=superuser_token_headers)
    assert r.status_code == 200
    body = r.json()
    logger.debug(f"List after delete: {body}")
    assert all(item["uid"] != uid for item in body["data"])  # filtered out

    # But appears when querying soft-deleted
    r = client.get(f"{settings.API_V1_STR}/designations/?is_deleted=true", headers=superuser_token_headers)
    assert r.status_code == 200
    body = r.json()
    logger.debug(f"List soft-deleted: {body}")
    assert any(item["uid"] == uid for item in body["data"])  # visible among deleted


def test_unique_short_code_conflict(client: TestClient, superuser_token_headers: dict[str, str]):
    short_code = fake.unique.lexify(text="SC-??????")
    p1 = {"title": fake.job(), "short_code": short_code, "remarks": fake.sentence(nb_words=3)}
    p2 = {"title": fake.job(), "short_code": short_code, "remarks": fake.sentence(nb_words=3)}

    r1 = client.post(f"{settings.API_V1_STR}/designations/", headers=superuser_token_headers, json=p1)
    assert r1.status_code == 200
    data1 = r1.json()
    logger.debug(f"First designation for unique test: {data1}")

    r2 = client.post(f"{settings.API_V1_STR}/designations/", headers=superuser_token_headers, json=p2)
    logger.info(f"Second designation (should conflict): {r2.json()}")
    # Expect unique constraint mapped to 409 with structured detail
    assert r2.status_code == 409
    body = r2.json()
    assert "detail" in body
    assert isinstance(body["detail"], list)
    # Clean up
    client.delete(f"{settings.API_V1_STR}/designations/{data1['uid']}", headers=superuser_token_headers)
