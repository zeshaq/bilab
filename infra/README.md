# infra/

bilab's own state store and deployment config. Clean-room from the lab — bilab
owns what lives here.

## What's here

- `docker-compose.yml` — bilab-postgres (the dashboard/chart state store),
  bound to 127.0.0.1:5435.

## Run

```bash
openssl rand -hex 24 > .env   # write BILAB_POSTGRES_PASSWORD=... if not present
docker compose up -d
```

The backend reads `BILAB_POSTGRES_PASSWORD` (or `BILAB_DATABASE_URL`) to connect.
Secrets live in `.env` (gitignored); only `.env.example` is committed.

## Notes

Identity (Keycloak) and policy (OPA) deliberately do NOT live here — bilab
delegates those to the lab (ADR-0007). This infra only holds bilab's own state.
