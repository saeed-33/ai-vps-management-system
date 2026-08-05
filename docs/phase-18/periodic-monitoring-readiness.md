# Periodic Monitoring Readiness

## Current Flow

1. The admin defines or selects a server.
2. The admin saves SSH settings for that server.
3. The admin can run an SSH test using the read-only `uptime` command.
4. A periodic monitoring cycle reads active servers from the server service.
5. The agent creates one logical server sub-agent per active server.
6. The agent collects read-only baseline metrics.
7. The API stores the cycle in memory and attempts PostgreSQL persistence.
8. The UI loads cycles from PostgreSQL when available, otherwise from memory.

## Database-Aware Behavior

The server service now attempts PostgreSQL first when `DATABASE_URL` is configured. If the database is unavailable, the service falls back to memory.

The following data is database-backed when PostgreSQL is ready:

- Servers.
- SSH access records in `server_credentials`.
- Monitoring cycles.
- Periodic monitoring reports.
- Monitoring metrics.

## SSH Test

Endpoint:

```text
POST /api/v1/servers/{server_id}/ssh-access/test
```

The test uses the allowed read-only `uptime` tool. It does not mutate the server.

## Remaining Constraints

- Secrets are stored as a foundation `secret_ref` payload in PostgreSQL when DB is enabled. This is not production-grade secret encryption.
- Docker image startup was not completed in this environment, so actual migration application remains an environment step.
- Real SSH cannot be verified without real server credentials.
