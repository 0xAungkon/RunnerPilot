from fastapi.testclient import TestClient
from app.core.config import settings
from faker import Faker

fake = Faker()


def random_lower_string() -> str:
    return fake.pystr(min_chars=32, max_chars=32).lower()


def random_email() -> str:
    return fake.email()

def get_tenant_token_headers(client: TestClient) -> dict[str, str]:
    
    r = client.post(f"{settings.API_V1_STR}/mock/tenants/dummy/tenant-token")
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers

