# semantic/

bilab's semantic layer — the governed metric model that every surface
(dashboards, Explore, the agent) resolves against. See docs/architecture.md and
ADR-0001.

## What's here

- `cube.js` — Cube config: connects to the lab's Trino (lakehouse catalog) as
  the governed svc-dataops identity, with a fresh Keycloak token per query.
- `token.js` — fetches a short-lived client_credentials token (secret from env).
- `model/*.yml` — the metric model: transactions, branches.
- `docker-compose.yml` — bilab's own Cube + Cubestore (pre-aggregation cache).
- `tests/test_semantic.py` — "same numbers everywhere" acceptance tests.

## Run (Phase 1, against the lab's Trino)

```bash
# 1. Provide the Trino CA cert (self-signed, not a secret):
mkdir -p tls && cp /home/system/datalab/trino/tls/trino.crt tls/trino.crt

# 2. Start the semantic layer (secret comes from the lab's env, never committed):
cd semantic
docker compose --env-file .env --env-file /home/system/datalab/dataops/.env up -d

# 3. Run the acceptance tests:
cd ..
set -a && . /home/system/datalab/dataops/.env && set +a
python -m pytest semantic/tests/test_semantic.py -v
```

Cube REST API: http://127.0.0.1:4199/cubejs-api/v1/ (Phase 1: loopback only,
dev mode; auth + gateway move here in Phase 3).

## Notes

- Phase 1 uses a single governed identity. Per-user RLS/token passthrough is
  Phase 3 (governance).
- `tls/trino.crt` and `.env` are gitignored; `tls/` needs the cert copied in.
