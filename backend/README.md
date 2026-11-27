# backend/

Python service: FastAPI. The API surface over the semantic layer, with an audit
trail. Every warehouse/semantic access is mediated here (ADR-0005).

## Run

```bash
cd backend
../.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Endpoints: `GET /health`, `GET /api/cubes`, `POST /api/query` (a Cube query).

## Test

```bash
cd .. && .venv/bin/pytest backend/tests/test_api.py -v
```

## Notes

- Auth (Keycloak/OPA) slots in ahead of these routes in Phase 3; the router is
  written so an auth dependency drops in without reshaping it.
- The audit log is a file-backed scaffold (`/tmp/bilab-audit.log`, override with
  `BILAB_AUDIT_LOG`); it moves to Postgres with retention + per-user identity in
  Phase 3/5.
