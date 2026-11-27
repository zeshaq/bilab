# semantic/

bilab's semantic layer — the governed metric model that every surface
(dashboards, Explore, the agent) resolves against. See docs/architecture.md,
ADR-0001 (Cube), and ADR-0007 (identity/policy delegation).

## What's here

- `cube.js` — Cube config: per-user governance. Every query runs AS THE PERSON
  (the backend verifies their Keycloak token and passes it in X-User /
  X-User-Token headers), so the lab's OPA masking/row filters apply. The cache
  is keyed per person.
- `model/*.yml` — the metric model: transactions, branches.
- `docker-compose.yml` — bilab's own Cube + Cubestore (pre-aggregation cache).
- `tests/test_semantic.py` — "same numbers everywhere" acceptance tests.

## Run (against the lab's Trino)

```bash
# 1. Provide the Trino CA cert (self-signed, not a secret):
mkdir -p tls && cp /home/system/datalab/trino/tls/trino.crt tls/trino.crt

# 2. Start the semantic layer (CUBEJS_API_SECRET from semantic/.env):
cd semantic
openssl rand -hex 32 > .env   # write CUBEJS_API_SECRET=... if not present
docker compose up -d

# 3. Run the acceptance tests (svc-dataops identity):
cd ..
set -a && . /home/system/datalab/dataops/.env && set +a
.venv/bin/pytest semantic/tests/test_semantic.py -v
```

Cube REST API: http://127.0.0.1:4199/cubejs-api/v1/ — requires X-User +
X-User-Token headers (the backend supplies them; Cube is not called directly in
normal operation).

## Notes

- Identity = Keycloak (lab realm); policy = OPA (lab, enforced at Trino).
  bilab owns neither (ADR-0007).
- `tls/trino.crt` and `.env` are gitignored; `tls/` needs the cert copied in.
