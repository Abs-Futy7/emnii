# ResolveOps Backend

FastAPI foundation for the ResolveOps multi-tenant customer support operations
platform. It currently exposes infrastructure and health checks only; business
features will be added in later iterations.

## Local setup

Run these commands from `backend/` in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `DATABASE_URL` in `.env` to a PostgreSQL SQLAlchemy URL, for example:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:your-password@localhost:5432/resolveops
```

The local fallback URL is
`postgresql+psycopg://postgres:postgres@localhost:5432/resolveops`. Do not use
development credentials in staging or production.

## Database migrations

Once PostgreSQL is running and `DATABASE_URL` is configured:

```powershell
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

The initial migration creates users, organizations, organization memberships,
client workspaces, and audit logs. Models exported from `app/db/models/` are
discovered through `app/db/base.py` and `alembic/env.py`.

The ownership hierarchy is:

```text
User ↔ OrganizationMembership ↔ Organization → Client
                                      └───────→ AuditLog
```

An organization is the ResolveOps tenant that owns users, permissions, and
billing boundaries. A client is a customer workspace managed by that tenant.
Keeping them separate lets one ResolveOps organization safely manage many client
workspaces without treating customer data as platform-user membership data.

## Run the API

```powershell
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`, interactive documentation at
`http://localhost:8000/docs`, and health at
`http://localhost:8000/api/v1/health`.

## Run checks

```powershell
pytest
ruff check .
python -m compileall app tests
```

## Structure

- `app/api/` defines routing and HTTP dependencies.
- `app/core/` owns configuration, logging, and shared exceptions.
- `app/db/` owns SQLAlchemy metadata, sessions, and future models.
- `app/schemas/` contains Pydantic transport models.
- `app/repositories/` will isolate database access.
- `app/services/` contains application orchestration outside route handlers.
- `app/domain/` is reserved for framework-independent business concepts.
- `app/utils/` contains small cross-cutting helpers.
- `tests/` contains pytest fixtures and automated tests.
- `alembic/` contains database migration configuration and revisions.

