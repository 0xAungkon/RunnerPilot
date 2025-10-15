# Runner Pillot - Github Action Runner Over the Fly

This repository contains the code for Runner Pilot, a system that allows you to manage GitHub Action runners on the fly. It provides a web interface to create, manage, and monitor self-hosted runners for your GitHub repositories with RBAC support & workspace management.

## Tech Stack:
- Backend: FastAPI , PostgreSQL, SQLModel, Alembic  , Redis, Celery
- Frontend: React, Tailwind CSS , Shadcn UI
- Containerization: Docker, Docker Compose
- Authentication: JWT
- In Memory Database: Redis
- Task Queue: Celery

## Database Schema:
* Common Fields (to be included in all tables):
  - created_at (Timestamp)
  - updated_at (Timestamp)
  - deleted_at (Timestamp, Nullable)
  - is_deleted (Boolean, Default: False)
  - is_active (Boolean, Default: True)

* Users Table:
  - uid (Primary Key)
  - full_name
  - email (Unique)
  - password (Hashed)

* Org Table:
  - uid (Primary Key) - str
  - name (Unique)
  - org type (Enum: personal, organization)
  - org creator (Foreign Key: Users.id)

* OrgUsers Table:
  - uid (Primary Key)
  - org_id (Foreign Key: Org.id)
  - user_id (Foreign Key: Users.id)
  - role (Enum: admin, member)
  - permissions (JSONB) # Example: {"create_runner": true, "delete_runner": false}

* Node Table:
  - uid (Primary Key)
  - name
  - ip_address (Nullable)
  - port (Nullable)
  - socket_path (Nullable)
  - type (Enum: Socket, Remote , Local)
  - status (Enum: active, inactive)
  - user_id (Foreign Key: Users.id)
  - org_id (Foreign Key: Org.id)

* Runners Table:
  - uid (Primary Key)
  - name
  - status (Enum: idle, busy)
  - user_id (Foreign Key: Users.id)
  - org_id (Foreign Key: Org.id)
  - docker_image (String) # Docker image to be used for the runner
  - github_repo (String) # GitHub repository the runner is associated with
  - github_runner_token (String) # Token provided by GitHub when registering the runner

* Runners Instance:
  - uid (Primary Key)
  - runner_id (Foreign Key: Runners.id)
  - node_id (Foreign Key: Node.id)
  - instance_identifier (String) # Unique identifier for the runner instance (e.g., container ID, VM ID)
  - instance_host (String) # Host where the instance is running (IP or hostname)
  - instance_meta (JSONB) # Metadata about the instance inspect
  - runner_id (Foreign Key: Runners.id)
  - status (Enum: online, offline, busy, idle)  # Maintain from Redis
  - last_heartbeat (Timestamp) # Last time the runner checked

* Monitoring Table:
  - uid (Primary Key)
  - runner_instance_id (Foreign Key: RunnersInstance.id)
  - cpu_usage (Float) # Percentage of CPU usage
  - memory_usage (Float) # Percentage of Memory usage
  - disk_usage (Float) # Percentage of Disk usage
  - timestamp (Timestamp) # Time of the monitoring data

Redis Data Structures:
* Runner Status:
  - Key: runner_status:{runner_instance_id}
  - Value: { "status": "online", "last_heartbeat": "2023-10-01T12:00:00Z" }
    - Expiry: 5 minutes (to automatically mark offline if no heartbeat)
* Runner Metrics:
  - Key: runner_metrics:{runner_instance_id}
  - Value: { "cpu_usage": 45.5, "memory_usage": 70.2, "disk_usage": 80.1 }
    - Expiry: 10 minutes (to keep recent metrics)
* Task Queue (using Celery with Redis as broker):
  - Tasks for registering/unregistering runners, sending heartbeats, and collecting metrics.
    - Example Task: register_runner(runner_instance_id)
    - Example Task: send_heartbeat(runner_instance_id)
    - Example Task: collect_metrics(runner_instance_id)

## Features:
- User Authentication & Authorization
- Organization Management
- RBAC (Role-Based Access Control)
- Node Management (Socket, Remote, Local)
- Runner Management (Create, Delete, Monitor)
- Real-time Monitoring of Runners
- Dockerized Deployment
- RESTful API with FastAPI
- Frontend Interface with React
- Background Task Processing with Celery

## Frontend Files Structure:
```
// Project Root
├── README.md                  // Project documentation
├── components.json            // Component configuration/metadata
├── eslint.config.js           // ESLint configuration
├── index.html                 // Main HTML entry
├── package-lock.json          // Exact dependency versions
├── package.json               // Project metadata & dependencies
├── public                     // Public/static assets
│   └── vite.svg               // Vite logo
├── src                        // Source code
│   ├── App.tsx                // Main React app component
│   ├── Routes.tsx             // App routing definitions
│   ├── assets                 // Static assets for app
│   │   └── react.svg          // React logo
│   ├── components             // Reusable UI components
│   │   ├── layouts            // Page layouts
│   │   │   ├── AuthLayout.tsx // Layout for auth pages
│   │   │   ├── CanvasLayout.tsx // Layout for canvas pages
│   │   │   ├── DashboardLayout.tsx // Layout for dashboard pages
│   │   │   └── fragments      // Layout sub-components
│   │   │       ├── Header.tsx // Header component
│   │   │       └── Navigation.tsx // Navigation component
│   │   ├── providers          // Context providers
│   │   │   ├── ThemeProvider.tsx // Theme context provider
│   │   │   └── ToastProvider.tsx // Toast/notification provider
│   │   ├── ui                 // UI components (Shadcn)
│   │   │   ├── accordion.tsx
│   │   │   ├── alert.tsx
│   │   │   └── ...            // Other UI components
│   │   └── utils              // Component utilities
│   │       └── theme-switcher.tsx // Theme switcher utility
│   ├── context                // React contexts
│   │   └── AuthContext.tsx    // Authentication context
│   ├── hooks                  // Custom hooks
│   │   └── use-mobile.ts      // Hook for mobile detection
│   ├── index.css               // Global CSS
│   ├── lib                     // Library utilities
│   │   ├── api
│   │   │   └── client.ts      // API client
│   │   ├── routes.ts           // Route definitions
│   │   └── utils.ts            // Helper utilities
│   ├── main.tsx               // React app entry
│   └── pages                  // Page components
│       ├── Authentication
│       │   ├── Login
│       │   │   ├── index.tsx  // Login page
│       │   │   └── service.tsx // Login services
│       │   └── Registration
│       │       ├── index.tsx  // Registration page
│       │       └── service.tsx // Registration services
│       ├── Dashboard
│       │   ├── Onboarding
│       │   │   ├── index.tsx
│       │   │   └── service.tsx
│       │   ├── Overview
│       │   │   ├── index.tsx
│       │   │   └── service.tsx
│       │   ├── Runners
│       │   │   ├── index.tsx
│       │   │   └── service.tsx
│       │   ├── Sample
│       │   │   ├── index.tsx
│       │   │   └── service.tsx
│       │   └── Test
│       │       └── index.tsx
│       └── ErrorPage.tsx      // Generic error page
├── tsconfig.app.json           // TypeScript config for app
├── tsconfig.json               // Base TypeScript config
├── tsconfig.node.json          // TypeScript config for Node
└── vite.config.ts              // Vite build configuration
```

## Backend Files Structure:
```
├── Dockerfile
├── Makefile
├── README.md
├── TODO.md
├── alembic.ini
├── app
│   ├── __init__.py
│   ├── admin
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── setup.py
│   │   └── views.py
│   ├── alembic
│   │   ├── README
│   │   ├── env.py
│   │   ├── script.py.mako
│   │   └── versions
│   │       └── fa9332c9ed8a_auto_migration.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── dependency
│   │   │   ├── Auth.py
│   │   │   ├── AuthHeaders.py
│   │   │   ├── AuthJWT.py
│   │   │   ├── State.py
│   │   │   └── __init__.py
│   │   ├── helpers
│   │   │   ├── __init__.py
│   │   │   └── common.py
│   │   ├── main.py
│   │   └── routes
│   │       ├── __init__.py
│   │       ├── common.py
│   │       ├── authentication.py
│   │       ├── designation.py
│   │       ├── employee.py
│   │       ├── health.py
│   │       ├── mock
│   │       │   ├── __init__.py
│   │       │   └── tenant.py
│   │       └── test.py
│   ├── backend_pre_start.py
│   ├── core
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── logging.py
│   │   └── security.py
│   ├── crud
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── users.py
│   │   ├── organization.py
│   │   └── .....other_crud_files.py
│   ├── initial_data.py
│   ├── main.py
│   ├── middlewares
│   │   └── AuthMiddleware.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── common.py
│   │   ├── department.py
│   │   ├── designation.py
│   │   └── employee.py
│   ├── tests
│   │   ├── __init__.py
│   │   ├── api
│   │   │   ├── __init__.py
│   │   │   └── routes
│   │   │       ├── __init__.py
│   │   │       ├── test_department.py
│   │   │       ├── test_designation.py
│   │   │       ├── test_employee.py
│   │   │       └── test_tenant.py
│   │   ├── conftest.py
│   │   ├── conftest_logging.py
│   │   ├── crud
│   │   │   ├── __init__.py
│   │   │   └── sampple_user.py
│   │   └── utils
│   │       ├── __init__.py
│   │       ├── item.py
│   │       ├── markdown_converter.py
│   │       ├── test_decorators.py
│   │       ├── test_logger.py
│   │       ├── user.py
│   │       └── utils.py
│   ├── tests_pre_start.py
│   └── utils
│       └── core.py
├── compose.yml
├── copier.yml
├── logs
│   ├── app.log
│   └── test_reports
│       └── test_report_20251014_170817.md
├── pipeline
│   └── dev-infra
│       ├── pgadmin
│       │   ├── compose.yml
│       │   └── dev.env
│       ├── postgresql
│       │   ├── compose.yml
│       │   └── dev.env
│       └── redis
│           └── compose.yml
├── pyproject.toml
├── scripts
│   ├── format.sh
│   ├── lint.sh
│   ├── prestart.sh
│   ├── run_tests_with_logging.py
│   ├── test.sh
│   ├── tests-start.sh
│   └── wipedb.py
└── uv.lock
```



API Documentation: 

User Authentication & Authorization:
- POST /auth/register: Register a new user.
- POST /auth/login: Authenticate a user and return a JWT token.
- POST /onboarding: Initial setup for the first user and organization.
- GET /common/me: Get the authenticated user's details.

- Organization Management:
- POST /org: Create a new organization.
- GET /org/{org_id}: Get details of a specific organization.
- GET /org: List all organizations the user belongs to.
- PUT /org/{org_id}: Update organization details.

- Runner Management:
- POST /org/{org_id}/runners: Create a new runner.
- GET /org/{org_id}/runners/{runner_id}: Get details of a specific runner.
- GET /org/{org_id}/runners: List all runners in the organization's workspace.
- DELETE /org/{org_id}/runners/{runner_id}: Delete a specific runner.
- PUT /org/{org_id}/runners/{runner_id}: Update runner details.
- PATCH /org/{org_id}/runners/{runner_id}/status: Update runner status (e.g., idle, busy).


- Runner Instance Management:
- POST /org/{org_id}/runners/{runner_id}/instance: Create a new runner.
- GET /org/{org_id}/runners/{runner_id}/instance/{instance_id}: Get details of a specific runner.
- GET /org/{org_id}/runners/{runner_id}/instance: List all runners in the organization's workspace.
- DELETE /org/{org_id}/runners/{runner_id}/instance/{instance_id}: Delete a specific runner.
- PUT /org/{org_id}/runners/{runner_id}/instance/{instance_id}: Update runner details.
- PATCH /org/{org_id}/runners/{runner_id}/instance/{instance_id}: Update runner status (e.g., idle, busy).

