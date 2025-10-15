import json
import os
from typing import Dict
from uuid import uuid4
from pydantic import BaseModel, Field, field_validator
from loguru import logger


class Common(BaseModel):
    name: str
    tenant_email: str
    plan: str


class PlanQuota(BaseModel):
    employees: int
    storage_gb: int
    workflow: int


class Usage(BaseModel):
    employees: int
    storage_gb: int
    workflow: int


class Tenant(BaseModel):
    status: bool
    readonly: bool
    common: Common
    plan_quota: PlanQuota
    usage: Usage

    @field_validator("usage")
    def validate_usage(cls, v, info):
        quota = info.data.get("plan_quota")
        if quota:
            if v.employees > quota.employees:
                raise ValueError("Employees usage exceeds quota")
            if v.storage_gb > quota.storage_gb:
                raise ValueError("Storage usage exceeds quota")
            if v.workflow > quota.workflow:
                raise ValueError("Workflow usage exceeds quota")
        return v


class Tenants(BaseModel):
    tenants: Dict[str, Tenant]


class MockTenantManager:
    def __init__(self):
        self.path_base_mock_data = "app/resources/mocks/initial/mock_tenents.json"
        self.path_user_mock_data = "app/resources/mocks/modified/mock_tenents.json"

        self.tenant_data = self.load_tenant_data()
        
    def get_path(self):
        return (
            self.path_user_mock_data
            if os.path.exists(self.path_user_mock_data)
            else self.path_base_mock_data
        )

    def load_tenant_data(self):
        with open(self.get_path(), "r") as f:
            data = json.load(f)
        return Tenants(**data).model_dump()

    def save_tenant_data(self):
        os.makedirs(os.path.dirname(self.path_user_mock_data), exist_ok=True)
        with open(self.path_user_mock_data, "w") as f:
            json.dump(self.tenant_data, f, indent=4)
            logger.info(f"Saved tenant data to {self.path_user_mock_data}")

    def add_tenant(self, tenant_info: dict, tenant_id: str = None) -> str:
        tenant_id = tenant_id or str(uuid4())
        if tenant_id in self.tenant_data["tenants"]:
            raise KeyError(f"Tenant ID {tenant_id} already exists")
        self.tenant_data["tenants"][tenant_id] = Tenant(**tenant_info).model_dump()
        self.save_tenant_data()
        return tenant_id

    def update_tenant(self, tenant_id: str, tenant_info: dict):
        if tenant_id not in self.tenant_data["tenants"]:
            raise KeyError(f"Tenant {tenant_id} not found")
        self.tenant_data["tenants"][tenant_id].update(Tenant(**tenant_info).model_dump())
        self.save_tenant_data()

    def delete_tenant(self, tenant_id: str):
        if tenant_id in self.tenant_data["tenants"]:
            del self.tenant_data["tenants"][tenant_id]
            self.save_tenant_data()
        else:
            raise KeyError(f"Tenant {tenant_id} not found")

    def list_tenants(self):
        return self.tenant_data


# if __name__ == "__main__":
#     manager = MockTenantManager()

#     # list tenants
#     print("All tenants:", manager.list_tenants())

#     # get tenant_id from user input
#     tenant_id = str(uuid4())


#     # add tenant
#     new_tenant = {
#         "status": True,
#         "readonly": False,
#         "common": {
#             "name": "Tenant Four",
#             "tenant_email": "tenant4@example.com",
#             "plan": "basic",
#         },
#         "plan_quota": {"employees": 50, "storage_gb": 50, "workflow": 50},
#         "usage": {"employees": 10, "storage_gb": 20, "workflow": 10},
#     }
#     tenant_id = manager.add_tenant(new_tenant, tenant_id=tenant_id)
#     print(f"Added tenant_id:{tenant_id} , info: {new_tenant}" )

#     # update tenant
#     update_data = {
#         "status": True,
#         "readonly": False,
#         "common": {
#             "name": "Tenant Four Updated",
#             "tenant_email": "tenant4@example.com",
#             "plan": "premium",
#         },
#         "plan_quota": {"employees": 100, "storage_gb": 200, "workflow": 100},
#         "usage": {"employees": 50, "storage_gb": 100, "workflow": 80},
#     }
#     manager.update_tenant(tenant_id, update_data)

#     # delete tenant
#     # manager.delete_tenant(tenant_id)

#     # final tenants
#     print("Updated tenants:", manager.list_tenants())
