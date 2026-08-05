# Phase 18: Periodic Monitoring Readiness Completion

## Goal

Make the periodic monitoring scope usable end-to-end before moving to report analysis.

## Required Work

- Let the API manage real servers through a database-aware repository.
- Keep memory fallback for local development when PostgreSQL is unavailable.
- Persist SSH access settings when PostgreSQL is available.
- Add an SSH connection test endpoint.
- Make the periodic monitoring agent read active servers from the server service.
- Load periodic monitoring cycles and reports from PostgreSQL when available.
- Update the admin panel server screen for adding servers, selecting a server, saving SSH access, and testing SSH.
- Add tests for the new server management behavior.

## Out of Scope

- Report analysis.
- Specialist agent activation.
- Solution generation or execution.
- Production-grade secret encryption.
- A dedicated secrets manager.
