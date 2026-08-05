# Phase 32: Completion Report

## Status

Completed.

## Completed Work

- Removed threshold fields from active monitoring profile schemas.
- Removed threshold-based report finding generation.
- Monitoring profiles now expose:
  - `monitoring_instructions`
  - `analysis_instructions`
  - `instructions_count`
- Added `MonitoringProfileCreate`.
- Added `POST /api/v1/monitoring-profiles`.
- Custom profiles are persisted in PostgreSQL through `monitoring_profiles` and `monitoring_profile_versions`.
- Added memory fallback only for local development when `DATABASE_URL` is not configured.
- Periodic monitoring now passes assigned profile instructions to the agent.
- SSH command policy is built from profile instructions.
- Raw snapshots include the instructions used for the report.
- Added LangGraph to `apps/agent`.
- Replaced the manual monitoring cycle loop with a LangGraph `StateGraph`.
- Updated the admin panel monitoring profiles page with tabs:
  - profile list
  - define instructions
- Updated tests for the instruction-based design.

## Verification

- `uv run --extra dev pytest` in `apps/agent`: passed, 8 tests.
- `uv run pytest` in `apps/api`: passed, 53 tests.
- `uv run python -m compileall src scripts` in `apps/api`: passed.
- `npm run lint` in `apps/admin-panel`: passed.
- `npm run build` in `apps/admin-panel`: passed.

## Notes

- Final report analysis remains LLM-only.
- Monitoring profile instructions are read-only by contract.
- The command allowlist is generated from the selected profile instructions.
- LangGraph is now the durable orchestration surface for later specialist-agent and solution-review stages.
