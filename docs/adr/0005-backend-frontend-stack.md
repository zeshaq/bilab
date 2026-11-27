# ADR-0005: Python backend + TypeScript frontend monorepo

Status: Accepted

## Context

bilab needs a backend (API, auth, orchestration, agent runtime) and a frontend
(dashboards, Explore, chat). We needed to choose languages and a repo layout.

## Decision

- Backend: Python, FastAPI + SQLAlchemy + Pydantic, in `backend/`.
- Frontend: TypeScript, React + ECharts + react-grid-layout, in `frontend/`.
- Semantic layer: Cube Core (Node.js), in `semantic/` — see ADR-0001.
- Single monorepo (`bilab`), with `infra/` for Docker Compose and deployment.

## Consequences

Positive:
- Python is the natural fit for the data ecosystem (SQLAlchemy dialects,
  Pydantic models, the agent/LangGraph stack) and matches the lab tooling.
- TypeScript/React is the default for modern BI frontends and has the best
  charting ecosystem (ECharts).
- Monorepo keeps cross-cutting changes (semantic model + backend + frontend)
  atomic and reviewable in one PR.

Negative:
- Polyglot: Python, TypeScript, and Node (Cube) in one repo. Accepted because
  each is the best tool for its layer, and the boundaries are clean (API for
  backend-frontend, SQL/MCP for semantic-backend).

## Alternatives considered

- Node/TypeScript backend: one language across frontend + backend, but weaker
  data/agent ecosystem than Python. Rejected.
- Separate repos per component: cleaner isolation but fragments changes across
  the semantic/backend/frontend boundary. Rejected for a single-team project.
