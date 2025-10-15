from unittest.mock import patch

from fastapi.testclient import TestClient
import pytest
from sqlmodel import Session

from app.core.config import settings
from app.core.logging import logger

@pytest.fixture
def get_tenant_access_token(client: TestClient) -> None:
    r = client.post(f"{settings.API_V1_STR}/mock/tenants/dummy/tenant-token")
    tokens = r.json()
    assert r.status_code == 200
    assert "access_token" in tokens
    assert tokens["access_token"]
    logger.info(f"Tenant access token: {tokens['access_token']}")
    yield tokens["access_token"]


def test_me_endpoint_with_tenant_token(client: TestClient, get_tenant_access_token):
    headers = {"Authorization": f"Bearer {get_tenant_access_token}"}
    r = client.get(f"{settings.API_V1_STR}/common/me", headers=headers)
    assert r.status_code == 200
    data = r.json()
    # The response is a user dict, not wrapped in "user"
    assert "user_type" in data
    assert data["user_type"] == "tenant_access_token"
    assert "tenant_id" in data
    assert data["tenant_id"] == data["identifier"]
    assert data["designation"] is None
    assert data["department"] is None
    assert data["is_active"] is True

def test_me_endpoint_unauthorized(client: TestClient):
    r = client.get(f"{settings.API_V1_STR}/common/me")
    assert r.status_code == 401
    assert "detail" in r.json()
