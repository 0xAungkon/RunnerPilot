# Service Boilerplate

This repository is a boilerplate for our microservices. It provides a solid foundation for building multi-tenant services using FastAPI, SQLModel, and PostgreSQL. The baseline includes CRUD patterns, authentication middleware, health endpoints, and developer tooling suitable for rapid iteration and consistent service scaffolding.

## Features

### Domain and Access Control
- Tenant aware data model with hierarchical relationships (tenant, company, department, designation, employee).
- Request level authorization supplied by a custom authentication middleware that decodes signed JWT payloads and decorates request state.
- Mock tenant manager and API helpers for generating tenant and employee tokens during development.

### Platform Capabilities
- FastAPI application with automatic router discovery and OpenAPI documentation.
- SQLModel ORM on top of PostgreSQL with Alembic migrations and connection retry using Tenacity.
- Loguru based structured logging streamed to stdout and `logs/app.log` with configurable log level.
- Optional Sentry integration for error tracking via `SENTRY_DSN`.
- System health, readiness, liveness, and metrics endpoints backed by psutil.

- Dependency management with `uv` and Python 3.10+ virtual environments.
- Makefile helpers for project setup, running the API, provisioning local infrastructure, managing migrations, and cleaning dev databases.
- Dockerfile with cached `uv` installation for reproducible container builds.
- Redis and pgAdmin docker compose definitions for local experimentation.

## Prerequisites
- Python 3.10 or newer.
- [`uv`](https://docs.astral.sh/uv/) for dependency management.
- Docker and Docker Compose (required for the provided infrastructure stacks or container builds).
- Optional: GNU Make for the convenience targets defined in the Makefile.

## Quick Start

1. **Clone and install dependencies**
   ```bash
   git clone <repository-url>
   cd FastAPI-boilerplate-oms
   cp .env.example .env
   uv sync
   source .venv/bin/activate
   ```

2. **Configure environment**
   - Update `.env` with database credentials, JWT secret, CORS origins, and Sentry DSN (if applicable).
   - Ensure `FRONTEND_HOST` and `BACKEND_CORS_ORIGINS` include the clients that will call the API.

3. **Start local infrastructure (optional but recommended)**
   ```bash
   make devInfra
   # or manually
   docker compose -f pipeline/dev-infra/postgresql/compose.yml up -d
   docker compose -f pipeline/dev-infra/redis/compose.yml up -d
   docker compose -f pipeline/dev-infra/pgadmin/compose.yml up -d
   ```

4. **Apply database migrations**
    - Using Make (auto-generate + upgrade):
       ```bash
       make migrate
       ```
    - Or manually with Alembic:
       ```bash
       uv run alembic upgrade head
       # To create a new revision manually
       uv run alembic revision --autogenerate -m "<message>"
       uv run alembic upgrade head
       ```

5. **Launch the API**
   ```bash
   uv run fastapi dev --reload app/main.py
   # equivalent Makefile helper
   make run
   ```

6. **Access the service**
   - API root: `http://localhost:8000/api/v1`
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`
   - Health endpoints: `http://localhost:8000/api/v1/health/`, `/ready`, `/live`, `/detailed`, `/metrics`

## Project Structure
```
alembic.ini               # Alembic configuration
copier.yml                # Template metadata for boilerplate generation
Dockerfile                # Container build definition using uv
Makefile                  # Setup, run, infra, lint/format, migrate, wipedb targets
pyproject.toml            # Project metadata and dependencies
uv.lock                   # Resolved dependency lockfile

app/
   main.py                 # FastAPI app setup and lifespan hooks
   api/
      main.py               # Router auto-loader
      routes/               # Common, health, mock, and domain routes
   core/                   # Config, DB engine/session, logging, security
   crud/                   # Class-based CRUD services and BaseCRUD
   middlewares/            # Auth middleware (JWT)
   models/                 # SQLModel ORM models and schemas (includes base.py)
   utils/                  # Startup hooks and external adapters
   alembic/                # Migration env and version scripts
   tests/                  # Pytest suites (api, crud, utils)
   resources/mocks/        # Mock fixtures for dev tokens/tenants

logs/
   app.log                 # Rotating application logs

pipeline/dev-infra/
   postgresql/             # Docker Compose for Postgres
   redis/                  # Docker Compose for Redis
   pgadmin/                # Docker Compose for pgAdmin

scripts/                  # Helper scripts (test, lint, format, prestart, wipedb)
```

## Local Development
- **Activate the environment**: `source .venv/bin/activate` after running `uv sync` or `make setup`.
- **Hot reload server**: `uv run fastapi dev --reload app/main.py` watches files and restarts the ASGI server on changes.
- **Database readiness**: The `scripts/prestart.sh` script waits for the database, applies migrations, and seeds initial data via `backend_pre_start.py` and `initial_data.py`.
- **Logging**: Logs stream to the console and rotate in `logs/app.log`. Adjust verbosity with `LOG_LEVEL` in `.env`.
- **Sentry**: Provide `SENTRY_DSN` and set `ENVIRONMENT` to `staging` or `production` to enable automatic error reporting.

### Database and Migrations
- Migration can be done via Make:
   - `make migrate` (optionally stamps, then autogenerates and upgrades to head)
- Or manually via Alembic:
   - Create revisions: `uv run alembic revision --autogenerate -m "add_new_table"`
   - Apply migrations: `uv run alembic upgrade head`
- The database engine is configured through environment variables (`POSTGRES_*`) and enforced in `Settings.SQLALCHEMY_DATABASE_URI`.

### Dev Database Cleaning
Use the following commands during development to reset your database state:

```bash
make wipedb   # Drops/cleans the dev database (uses scripts/wipedb.py)
make migrate  # Recreate schema by generating and applying migrations
```

### Mock Tenant Manager and Token Utilities
- Development friendly endpoints live under `/api/v1/mock/tenants` and wrap `MockTenantManager`.
- Base JSON fixtures reside in `app/resources/mocks/initial/mock_tenents.json`; modified data is persisted to `app/resources/mocks/modified/mock_tenents.json`.
- Use the mock routes to add tenants and mint access tokens for tenants or employees without integrating with an external identity provider.

## Testing and Quality
- Run the full suite with `bash scripts/test.sh` (coverage is captured in `htmlcov/index.html`).
- Direct `pytest` invocation: `uv run pytest`.
- Linting: `uv run ruff check app/`.
- Type checks: `uv run mypy app/`.
- Formatting: `uv run black app/` or `bash scripts/format.sh` to apply autoflake and black.

## Docker Support
- Build the image: `docker build -t employee-service .`.
- Run the container:
  ```bash
  docker run --env-file .env -p 8000:8000 employee-service
  ```
- The container entrypoint executes `fastapi run --workers 4 app/main.py`. Mount the project directory and override the command if you need live reload inside the container during development.

## Authentication and Authorization
- All protected endpoints rely on a `Bearer <JWT>` header. The middleware decodes the token using `SECRET_KEY` and algorithm `HS256`.
- The JWT `sub` claim must be a JSON string matching `JWTUserScheme`:
  ```json
  {
    "identifier": "<user-or-tenant-uuid>",
    "user_type": "tenant_access_token" | "employee_access_token",
    "tenant_id": "<tenant-uuid>",
    "designation": "<optional-designation>",
    "department": "<optional-department>",
    "is_active": true
  }
  ```
- `tenant_access_token` grants visibility across the tenant; `employee_access_token` constrains queries to the user's `tenant_id`.
- Tokens can be generated via the mock endpoints or issued by your identity provider so long as they are signed with the configured `SECRET_KEY`.

## API Highlights
- `GET /api/v1/health/*` - liveness, readiness, detailed system metrics.
- `GET /api/v1/common/me` - return the decoded user attached by the authentication middleware.
- `CRUD /api/v1/tenants` - multi-tenant management (tenant level tokens required).
- `CRUD /api/v1/companies` - tenant scoped companies.
- `CRUD /api/v1/departments`, `CRUD /api/v1/designations`, `CRUD /api/v1/employees` - employee domain management.
- `/api/v1/mock/tenants/*` - fixtures and token helpers for development flows.

## Configuration Reference
Key environment variables defined in `.env.example`:
- `ENVIRONMENT`: `local`, `staging`, or `production`; toggles Sentry initialization and warnings for default secrets.
- `PROJECT_NAME`, `SERVICE_NAME`: Applied to OpenAPI metadata and logging.
- `SECRET_KEY`: Used to sign JWTs. Replace the default before deploying.
- `BACKEND_CORS_ORIGINS`, `FRONTEND_HOST`: Controls allowed origins for CORS and link generation.
- `POSTGRES_SERVER`, `POSTGRES_PORT`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`: Database connection details.
- `SENTRY_DSN`: Enable error reporting when non-empty.
- `SMTP_*`, `EMAILS_FROM_EMAIL`: Configure transactional email support if required.

## Troubleshooting
- **Database connection errors**: Verify the Postgres container is healthy (`docker ps`, `docker logs postgres-dev`) and the `.env` credentials match the compose files.
- **Unauthorized responses**: Ensure the JWT is signed with the same `SECRET_KEY` and contains a valid JSON payload in the `sub` claim according to `JWTUserScheme`.
- **Missing system metrics**: Install `psutil` in the environment or include it in your deployment image; without it the `/metrics` endpoint will return placeholders.
- **Migrations not applying**: Confirm Alembic revisions exist in `app/alembic/versions` and that the `TENANT_SCOPE` configuration is not blocking required schemas.

---

For additional automation or integration patterns, refer to the scripts under `scripts/` and the infrastructure blueprints inside `pipeline/dev-infra/`.
