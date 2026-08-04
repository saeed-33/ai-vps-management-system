# Control Plane API

FastAPI service for the AI VPS Management System control plane.

## Current Scope

This is the phase 4 foundation. It provides:

- Application factory.
- Central settings.
- Health endpoints.
- API v1 router.
- Metadata endpoint.
- Async SQLAlchemy database readiness check.
- Bootstrap auth foundation.
- Smoke tests.

It does not yet provide auth, RBAC, CRUD, MCP, or agent integration.

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
```
