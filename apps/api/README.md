# Control Plane API

FastAPI service for the AI VPS Management System control plane.

## Current Scope

This is the phase 9 foundation. It provides:

- Application factory.
- Central settings.
- Health endpoints.
- API v1 router.
- Metadata endpoint.
- Async SQLAlchemy database readiness check.
- Bootstrap auth foundation.
- Users and roles foundation endpoints.
- Servers foundation endpoints.
- Monitoring profiles foundation endpoints.
- Smoke tests.

It does not yet provide database-backed CRUD, MCP, or agent integration.

## Install

```bash
uv sync --extra dev
```

## Run

```bash
uv run uvicorn control_plane_api.main:app --reload --host 127.0.0.1 --port 8000
```

## Test

```bash
uv run pytest
```

## Bootstrap Admin Password Hash

```bash
uv run python scripts/hash_password.py
```

Set the result in:

```text
BOOTSTRAP_ADMIN_PASSWORD_HASH=
```

## Endpoints

```text
GET /health/live
GET /health/ready
GET /api/v1/meta
POST /api/v1/auth/token
GET /api/v1/auth/me
GET /api/v1/auth/rbac
GET /api/v1/users
GET /api/v1/users/me
GET /api/v1/users/roles
GET /api/v1/servers
GET /api/v1/servers/summary
GET /api/v1/servers/{server_id}
GET /api/v1/monitoring-profiles
GET /api/v1/monitoring-profiles/summary
GET /api/v1/monitoring-profiles/{profile_id}
```
