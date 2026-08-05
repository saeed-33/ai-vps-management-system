# Phase 20: Database Persistence Enforcement

## Goal

Stop silent memory fallback when PostgreSQL is configured but unavailable, and make server persistence status visible.

## Required Work

- Diagnose why added servers disappeared after API restart.
- Run the project PostgreSQL database.
- Apply the initial schema migration.
- Point the API to the project database.
- Prevent silent memory persistence when `DATABASE_URL` is configured.
- Make the server source visible in the admin panel.
- Ensure routes use app-scoped settings instead of reading `.env` directly during tests.

## Out of Scope

- Recovering servers that were previously saved only in memory.
- Production secret management.
- Report analysis.
