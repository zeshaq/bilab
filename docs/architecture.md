# Architecture

bilab is a warehouse-native BI tool with a governed semantic layer at its core.
Every surface — dashboards, Explore, the AI agent — resolves against the same
semantic model, so humans and agents always get the same numbers.

## Principles

1. Semantic layer is the source of truth. Metrics, dimensions, joins, and
   security are defined once, centrally, and versioned. No surface defines its
   own metric logic.
2. Warehouse-native. bilab queries data in place (Trino/Iceberg, Snowflake,
   BigQuery, Postgres, DuckDB). It does not copy or ETL data into its own store.
3. Agent-native. The AI agent is a first-class interface built on the same
   governed semantic layer, exposed over the Model Context Protocol (MCP).
4. Single security context. Authentication (who you are) and authorization
   (what you may see) are applied identically to humans and agents. Row-level
   security is enforced at the semantic layer, not per-dashboard.

## Component architecture

```
                          +-----------------------------+
                          |        Frontend (React)      |
                          |  Dashboards | Explore | Chat |
                          +--------------+---------------+
                                         | REST / WebSocket
                          +--------------v---------------+
                          |      Backend (FastAPI)       |
                          |  API, orchestration, auth,   |
                          |  job queue, agent runtime    |
                          +------+----------------+------+
                                 |                |
                     +-----------v----+    +------v------------+
                     |  Semantic layer|    |  Agent (LangGraph)|
                     |  (Cube Core)   |<---+  MCP tools        |
                     |  metrics, RLS, |    |  BYOK (LiteLLM)   |
                     |  pre-aggregation|   +-------------------+
                     +--------+-------+
                              | SQL (query in place)
                +-------------+-------------+
                |  Warehouse of record      |
                |  Trino/Iceberg, Snowflake,|
                |  BigQuery, Postgres,      |
                |  DuckDB                    |
                +---------------------------+

Cross-cutting:
  AuthN: Keycloak (OIDC/SAML/LDAP)
  AuthZ: OPA/Casbin (fine-grained), RLS in semantic layer
  Cache: Redis + Cube pre-aggregations (ClickHouse/DuckDB)
  Jobs:  Celery + Redis (scheduling, alerts)
  Metadata: OpenMetadata (lineage, glossary)
  Observability: OpenTelemetry + Prometheus/Grafana
```

## Component responsibilities

- Frontend (React + TypeScript + ECharts + react-grid-layout): dashboards,
  Explore (ad-hoc analysis), embedded SDK, chat panel. Thin — no metric logic,
  no direct warehouse queries; it talks to the backend, which talks to the
  semantic layer.
- Backend (FastAPI + SQLAlchemy + Pydantic): API surface, authentication,
  authorization decisions, query orchestration, scheduling/alerts, agent
  runtime, audit logging. All warehouse access is mediated here.
- Semantic layer (Cube Core): metric and dimension definitions, joins,
  row-level security via security context, pre-aggregation caching. Exposes
  the model over SQL (Postgres-compatible), REST, GraphQL, and MCP.
- Agent (LangGraph): multi-step agent (ask -> explore -> chart -> dashboard ->
  schedule). Calls MCP tools that wrap the semantic layer. BYOK via LiteLLM.
- Warehouse: data of record; queried in place, never copied.

## Data flow (a user question)

1. User asks a question in natural language (chat) or builds a chart (Explore).
2. Backend resolves the request against the semantic layer (metrics, dimensions,
   security context).
3. Semantic layer compiles to SQL against the warehouse and executes (with
   pre-aggregation cache where applicable).
4. Result returns as governed data; the frontend renders it.

An agent follows the same path through MCP tools — the only difference is that
the "user" is an LLM, subject to the same RBAC and RLS.

## Key decisions

Architecture-level decisions are recorded as ADRs in [docs/adr/](adr/). The
important ones:

- [0001 — Cube Core as the semantic layer](adr/0001-cube-as-semantic-layer.md)
- [0002 — Not using Grafana Scene](adr/0002-not-grafana-scene.md)
- [0003 — MCP as the agent interface](adr/0003-mcp-as-agent-interface.md)
- [0004 — Warehouse-native (no data copy)](adr/0004-warehouse-native.md)
- [0005 — Python backend + TypeScript frontend monorepo](adr/0005-backend-frontend-stack.md)
