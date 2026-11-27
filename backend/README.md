# backend/

Python service: FastAPI. The API surface over the semantic layer, with
per-user authentication and an audit trail. Every warehouse/semantic access is
mediated here (ADR-0005); identity is Keycloak and policy is OPA (ADR-0007).

## Run

```bash
cd backend
../.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Endpoints:
- `GET /health` — public
- `POST /api/login` — exchange username/password for a Keycloak token
- `GET /api/cubes` — list cubes (requires bearer token)
- `POST /api/query` — run a Cube query AS THE CALLER (requires bearer token)

## Test

```bash
cd ..
set -a && . /home/system/datalab/dataops/.env && . /home/system/datalab/identity/.env && set +a
.venv/bin/pytest backend/tests/ -v
```

## Notes

- The Keycloak token is verified (signature RS256 via JWKS, issuer, audience)
  before the identity is trusted; the token is then forwarded to Cube so OPA
  masking/row filters apply at Trino.
- The audit log is file-backed (`/tmp/bilab-audit.log`, override with
  `BILAB_AUDIT_LOG`) and records the caller's identity; it moves to Postgres
  with retention in Phase 5.
- Phase 3 login uses the resource-owner password grant; the browser OIDC
  redirect flow is the production path and slots in without reshaping the API.
