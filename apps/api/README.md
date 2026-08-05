# Control Plane API

FastAPI service for the AI VPS Management System control plane.

## Current Scope

This is the phase 13 foundation. It provides:

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
- Specialist agents foundation endpoints.
- Allowed tools foundation endpoints.
- Periodic monitoring report foundation endpoints.
- Periodic monitoring scheduler foundation endpoints.
- Integration with the local `ai-vps-agent` package for report collection.
- Optional PostgreSQL persistence for periodic monitoring reports.
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

The current super admin is a bootstrap admin loaded from environment variables. It is not a database user yet.

```bash
uv run python scripts/hash_password.py
```

Set the result in:

```text
BOOTSTRAP_ADMIN_PASSWORD_HASH=
```

Required auth environment:

```env
AUTH_SECRET_KEY=change_me_to_a_long_random_value
BOOTSTRAP_ADMIN_EMAIL=admin@example.com
BOOTSTRAP_ADMIN_PASSWORD_HASH=generated_hash_here
```

Use `BOOTSTRAP_ADMIN_EMAIL` and the original password used to generate the hash on `/login`.

## LLM-Only Periodic Report Analysis

Periodic monitoring report analysis is produced by LLM only. Rule-based threshold checks are used as internal signals for the LLM prompt, but they are not emitted as the final report analysis.

To produce final analysis reports locally, run Ollama and set:

```env
LLM_ANALYSIS_ENABLED=true
LLM_ANALYSIS_PROVIDER=ollama
LLM_ANALYSIS_MODEL=llama3.1
LLM_ANALYSIS_BASE_URL=http://127.0.0.1:11434
LLM_ANALYSIS_TIMEOUT_SECONDS=20
```

If LLM is disabled or the LLM call fails, the monitoring cycle still completes, but the analysis report status becomes `analysis_unavailable` or `analysis_failed`. No rule-based fallback is emitted as final analysis.

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
PUT /api/v1/servers/{server_id}/ssh-access
GET /api/v1/monitoring-profiles
GET /api/v1/monitoring-profiles/summary
GET /api/v1/monitoring-profiles/{profile_id}
GET /api/v1/specialist-agents
GET /api/v1/specialist-agents/summary
GET /api/v1/specialist-agents/{agent_id}
GET /api/v1/allowed-tools
GET /api/v1/allowed-tools/summary
GET /api/v1/allowed-tools/{tool_id}
POST /api/v1/periodic-monitoring/cycles
GET /api/v1/periodic-monitoring/cycles
GET /api/v1/periodic-monitoring/cycles/latest
GET /api/v1/periodic-monitoring/reports
GET /api/v1/periodic-monitoring/analysis-reports
POST /api/v1/periodic-monitoring/scheduler/start
POST /api/v1/periodic-monitoring/scheduler/stop
GET /api/v1/periodic-monitoring/scheduler/status
```
