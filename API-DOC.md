# Runner Pilot API Documentation

---

## 1. User Authentication & Authorization

### POST /auth/register

**Description:** Register a new user.
**Request:**

```json
{
  "full_name": "John Doe",
  "email": "john@example.com",
  "password": "strongpassword"
}
```

**Authentication:** Not required
**Response 200:**

```json
{
  "uid": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "full_name": "John Doe",
  "email": "john@example.com",
  "created_at": "2025-10-15T12:00:00Z"
}
```

---

### POST /auth/login

**Description:** Authenticate a user and return a JWT token.
**Request:**

```json
{
  "email": "john@example.com",
  "password": "strongpassword"
}
```

**Authentication:** Not required
**Response 200:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600
}
```

---


### POST /onboarding

**Description:** Initial setup for the first organization.
**Authentication:** Required (Bearer Token)
**Request:**

```json
{
  "organization": {
    "name": "Gigatech",
    "short_name": "GT",
    "type": "personal"
  }
}
```

**Response 200:**

```json
{
  "organization": {
    "name": "Gigatech",
    "short_name": "GT",
    "type": "personal",
    "created_at": "2025-10-15T12:00:00Z"
  }
}
```

---

### GET /common/me

**Description:** Get the authenticated user's details.
**Authentication:** Required (Bearer Token)
**Response 200:**

```json
{
  "uid": "a1b2c3d4-5678-90ab-cdef-1234567890ab",
  "full_name": "John Doe",
  "email": "john@example.com",
  "created_at": "2025-10-15T12:00:00Z",
  "organizations": [
    {
      "short_name": "GT",
      "name": "Gigatech"
    },
    {
      "short_name": "NT",
      "name": "NextTech"
    }
  ]
}

```

---

## 2. Organization Management

### POST /org

**Description:** Create a new organization.
**Authentication:** Required
**Request:**

```json
{
  "name": "Gigatech",
  "short_name": "GT",
  "type": "organization"
}
```

**Response 200:**

```json
{
  "name": "Gigatech",
  "short_name": "GT",
  "type": "organization",
  "created_at": "2025-10-15T12:00:00Z"
}
```

### GET /org/{org_id}

**Description:** Get organization details.
**Authentication:** Required
**Response 200:**

```json
{
  "name": "Gigatech",
  "short_name": "GT",
  "type": "organization",
  "created_at": "2025-10-15T12:00:00Z"
}
```

### GET /org

**Description:** List all organizations the user belongs to.
**Authentication:** Required
**Response 200:**

```json
[
  {
    "name": "Gigatech",
    "short_name": "GT",
    "type": "organization"
  },
  {
    "name": "NextTech",
    "short_name": "NT",
    "type": "personal"
  }
]
```

### PUT /org/{org_id}

**Description:** Update organization details.
**Authentication:** Required
**Request:**

```json
{
  "name": "Gigatech Updated"
}
```

**Response 200:**

```json
{
  "name": "Gigatech Updated",
  "short_name": "GT",
  "type": "organization"
}
```

---

## 3. Node Management

### POST /org/{org_id}/nodes

**Description:** Create a new node.
**Authentication:** Required
**Request:**

```json
{
  "name": "Node-01",
  "type": "Remote",
  "ip_address": "192.168.1.10",
  "port": 22
}
```

**Response 200:**

```json
{
  "uid": "f1e2d3c4-5678-90ab-cdef-1234567890ef",
  "name": "Node-01",
  "type": "Remote",
  "ip_address": "192.168.1.10",
  "port": 22,
  "status": "active",
  "created_at": "2025-10-15T12:05:00Z"
}
```

### GET /org/{org_id}/nodes

**Description:** List all nodes in the organization.
**Authentication:** Required
**Response 200:**

```json
[
  {
    "uid": "f1e2d3c4-5678-90ab-cdef-1234567890ef",
    "name": "Node-01",
    "type": "Remote",
    "status": "active"
  },
  {
    "uid": "a1b2c3d4-5678-90ab-cdef-1234567890ff",
    "name": "Node-02",
    "type": "Socket",
    "status": "inactive"
  }
]
```

### GET /org/{org_id}/nodes/{node_id}

**Description:** Get details of a specific node.
**Authentication:** Required
**Response 200:**

```json
{
  "uid": "f1e2d3c4-5678-90ab-cdef-1234567890ef",
  "name": "Node-01",
  "type": "Remote",
  "ip_address": "192.168.1.10",
  "port": 22,
  "status": "active",
  "created_at": "2025-10-15T12:05:00Z"
}
```

### PUT /org/{org_id}/nodes/{node_id}

**Description:** Update node details.
**Authentication:** Required
**Request:**

```json
{
  "name": "Node-01-Updated",
  "status": "inactive"
}
```

**Response 200:**

```json
{
  "uid": "f1e2d3c4-5678-90ab-cdef-1234567890ef",
  "name": "Node-01-Updated",
  "type": "Remote",
  "status": "inactive"
}
```

### DELETE /org/{org_id}/nodes/{node_id}

**Description:** Delete a node.
**Authentication:** Required
**Response 200:**

```json
{
  "message": "Node deleted successfully."
}
```

---

## 4. Runner Management

### POST /org/{org_id}/runners

**Description:** Create a new runner.
**Authentication:** Required
**Request:**

```json
{
  "name": "Runner-01",
  "docker_image": "ubuntu:22.04",
  "github_repo": "Gigatech/my-repo",
  "github_runner_token": "ghr_1234567890abcdef"
}
```

**Response 200:**

```json
{
  "uid": "r1u2n3e4-5678-90ab-cdef-1234567890ab",
  "name": "Runner-01",
  "status": "idle",
  "docker_image": "ubuntu:22.04",
  "github_repo": "Gigatech/my-repo",
  "github_runner_token": "ghr_1234567890abcdef",
  "created_at": "2025-10-15T12:10:00Z"
}

```

### GET /org/{org_id}/runners

**Description:** List all runners.
**Authentication:** Required
**Response 200:**

```json
[
  {
    "uid": "r1u2n3e4-5678-90ab-cdef-1234567890ab",
    "name": "Runner-01",
    "github_runner_token": "ghr_1234567890abcdef",
    "status": "idle"
    
  }
]
```

### GET /org/{org_id}/runners/{runner_id}

**Description:** Get details of a specific runner.
**Authentication:** Required
**Response 200:**

```json
{
  "uid": "r1u2n3e4-5678-90ab-cdef-1234567890ab",
  "name": "Runner-01",
  "status": "idle",
  "docker_image": "ubuntu:22.04",
  "github_repo": "Gigatech/my-repo",
    "github_runner_token": "ghr_1234567890abcdef",
}
```

### PUT /org/{org_id}/runners/{runner_id}

**Description:** Update runner details.
**Authentication:** Required
**Request:**

```json
{
  "name": "Runner-01-Updated",
    "github_runner_token": "ghr_1234567890abcdef",
}
```

**Response 200:**

```json
{
  "uid": "r1u2n3e4-5678-90ab-cdef-1234567890ab",
    "github_runner_token": "ghr_1234567890abcdef",
  "name": "Runner-01-Updated",
  "status": "idle"
}
```

### DELETE /org/{org_id}/runners/{runner_id}

**Description:** Delete a runner.
**Authentication:** Required
**Response 200:**

```json
{
  "message": "Runner deleted successfully."
}
```

---

## 5. Runner Instance Management

### POST /org/{org_id}/runners/{runner_id}/instance

**Description:** Create a new runner instance.
**Authentication:** Required
**Request:**

```json
{
  "node_id": "f1e2d3c4-5678-90ab-cdef-1234567890ef",
}
```

**Response 200:**

```json
{
  "uid": "i1n2s3t4-5678-90ab-cdef-1234567890ab",
  "runner": {"uid": "r1u2n3e4-5678-90ab-cdef-1234567890ab", "name": "Runner-01"},
  "node": {"uid": "f1e2d3c4-5678-90ab-cdef-1234567890ef", "name": "Node-01"},
  "instance_identifier": "container_01",
  "instance_host": "192.168.1.10",
  "status": "online",
  "last_heartbeat": "2025-10-15T12:15:00Z"
}
```

### GET /org/{org_id}/runners/{runner_id}/instance

**Description:** List all runner instances for a runner.
**Authentication:** Required
**Response 200:**

```json
[
  {
    "uid": "i1n2s3t4-5678-90ab-cdef-1234567890ab",
    "instance_identifier": "container_01",
    "instance_host": "192.168.1.10",
    "status": "online"
  }
]
```

### GET /org/{org_id}/runners/{runner_id}/instance/{instance_id}

**Description:** Get details of a specific runner instance.
**Authentication:** Required
**Response 200:**

```json
{
  "uid": "i1n2s3t4-5678-90ab-cdef-1234567890ab",
  "runner": {"uid": "r1u2n3e4-5678-90ab-cdef-1234567890ab", "name": "Runner-01"},
  "node": {"uid": "f1e2d3c4-5678-90ab-cdef-1234567890ef", "name": "Node-01"},
  "instance_identifier": "container_01",
  "instance_host": "192.168.1.10",
  "status": "online",
  "last_heartbeat": "2025-10-15T12:15:00Z"
}
```


### DELETE /org/{org_id}/runners/{runner_id}/instance/{instance_id}

**Description:** Delete a runner instance.
**Authentication:** Required
**Response 200:**

```json
{
  "message": "Runner instance deleted successfully."
}
```

## 6. Monitoring

### GET /org/{org_id}/runners/{runner_id}/instance/{instance_id}/metrics

**Description:** Get real-time metrics for a runner instance.
**Authentication:** Required
**Response 200:**

```json
{
  "cpu_usage": 45.5,
  "memory_usage": 70.2,
  "disk_usage": 80.1,
  "timestamp": "2025-10-15T12:20:00Z"
}
```

### GET /org/{org_id}/runners/{runner_id}/instance/{instance_id}/logs

**Description:** Get recent logs for a runner instance.
**Authentication:** Required
**Response 200:**

```json
[
  {
    "timestamp": "2025-10-15T12:18:00Z",
    "level": "INFO",
    "message": "Runner container started successfully."
  },
  {
    "timestamp": "2025-10-15T12:19:00Z",
    "level": "WARN",
    "message": "Runner heartbeat delayed."
  }
]
```

