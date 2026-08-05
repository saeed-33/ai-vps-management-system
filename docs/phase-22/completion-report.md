# Phase 22 Completion Report: Periodic Monitoring Server UUID Persistence Fix

## Status

Completed.

## Root Cause

Periodic monitoring persistence always converted `report.server_id` through UUID v5. For database-backed servers, `report.server_id` is already a real UUID. Re-hashing it produced a different server id and caused PostgreSQL to try inserting a duplicate server name, which failed on `servers_name_key`.

## Completed Work

- Added `database_uuid`.
- Preserved existing UUID server ids during report persistence.
- Kept UUID v5 mapping only for legacy text ids.
- Added a regression test.

## Verification

- `uv run pytest` in `apps/api`: passed, `48 passed`.
- `uv run python -m compileall src scripts` in `apps/api`: passed.
- `GET /health/ready`: ready.
