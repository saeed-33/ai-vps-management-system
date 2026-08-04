# Database Package

This package contains the database schema and migrations for the AI VPS Management System.

## Current Approach

The project starts with plain PostgreSQL migrations. An ORM can be introduced later after the API stack is finalized.

## Development Database

Use the development compose file:

```bash
docker compose -f infra/compose/docker-compose.dev.yml up -d postgres redis
```

Apply the initial migration manually for now:

```bash
psql "$DATABASE_URL" -f packages/database/migrations/0001_initial_schema.sql
```

## Extensions

The initial migration enables:

- `pgcrypto` for `gen_random_uuid()`.
- `vector` for RAG embeddings through pgvector.

The development PostgreSQL image must include pgvector.
