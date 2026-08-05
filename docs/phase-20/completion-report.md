# Phase 20 Completion Report: Database Persistence Enforcement

## Status

Completed.

## Root Cause

The API had `DATABASE_URL` configured for `localhost:5432`, but that PostgreSQL instance rejected the configured password. Because server management had a memory fallback, added servers appeared to save successfully but were only stored in API memory. Restarting the backend cleared them.

## Completed Work

- Started the project PostgreSQL container on host port `55432`.
- Applied `packages/database/migrations/0001_initial_schema.sql`.
- Updated local `apps/api/.env` to use:

```text
postgresql://postgres:change_me@localhost:55432/ai_vps_management
```

- Verified `GET /health/ready` returns `ready=true`.
- Changed server create/update/SSH save behavior:
  - if `DATABASE_URL` is empty, local memory fallback is allowed;
  - if `DATABASE_URL` is configured and persistence fails, the API returns `503` instead of silently saving to memory.
- Changed server and periodic monitoring routes to use app-scoped settings.
- Displayed server `source` in the admin panel.

## Verification

- `uv run pytest` in `apps/api`: passed, `47 passed`.
- `uv run python -m compileall src scripts` in `apps/api`: passed.
- `npm run lint`: passed.
- PostgreSQL container: `ai-vps-postgres-dev`, healthy, `55432 -> 5432`.
- `GET /health/ready`: `200`, ready.

## Important Note

Servers added before this fix were saved only in memory and cannot be recovered after backend restart. Add them again now; new servers should show `source: database` in the `/servers` page.
