# Development Compose

Start local dependencies:

```bash
docker compose -f infra/compose/docker-compose.dev.yml up -d
```

Stop local dependencies:

```bash
docker compose -f infra/compose/docker-compose.dev.yml down
```

Remove local volumes:

```bash
docker compose -f infra/compose/docker-compose.dev.yml down -v
```

Apply the initial database migration:

```bash
psql "$DATABASE_URL" -f packages/database/migrations/0001_initial_schema.sql
```

The development PostgreSQL service uses `pgvector/pgvector:pg16` so the `vector` extension is available.
