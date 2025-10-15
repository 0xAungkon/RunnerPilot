import json

# Sample Structure of mock_tenants.json
# {
#  "tenant_id1":{
#             "status": true,
#             "readonly": false,
#             "common":{
#                 "name": "Tenant One",
#                 "tenant_email": "tenant1.example.com",
#                 "plan": "basic"
#             },
#             "plan_quota": {
#                 "employees": 10,
#                 "storage_gb": 10,
#                 "workflow": 10
#             },
#             "usage": {
#                 "employees": 10,
#                 "storage_gb": 20,
#                 "workflow": 5
#             }
#         },
# }

def load_tenant_data(self):
        with open("app/additional_data/mock_tenants.json") as f:
            data = json.load(f)
        return data.get("tenants", {}).get(self.tenant_id, {})
    
all_tenant_data = load_tenant_data()



class TenantManager:
    def __init__(self, tenant_id: str):
        # Initialize other necessary attributes
        self.tenant_id = tenant_id
        self.tenant_data = self.pull_tenant_data()

    def pull_tenant_data(self):
        return all_tenant_data.get(self.tenant_id, {})  # TODO: will be pull from redis

    def get_tenant_info(self):
        return self.tenant_data.get("common", {})

    def add_employee(self):
        tenant = self.tenant_data.get("tenants", {}).get(self.tenant_id, {})
        if tenant:
            if tenant["usage"]["employees"] < tenant["plan_quota"]["employees"]:
                tenant["usage"]["employees"] += 1
                return True
            else:
                return False
        return False
    
    def remove_employee(self): 
        tenant = self.tenant_data.get("tenants", {}).get(self.tenant_id, {})
        if tenant and tenant["usage"]["employees"] > 0:
            tenant["usage"]["employees"] -= 1
            return True
        return False
    
    def can_add_employee(self):
        tenant = self.tenant_data.get("tenants", {}).get(self.tenant_id, {})
        if tenant:
            return tenant["usage"]["employees"] < tenant["plan_quota"]["employees"]
        return False