# bilab

A semantic-layer-first, agent-native business intelligence tool.

## What it is

bilab competes on three things commercial BI tools bolt on after the fact:

1. Semantic layer first — metrics are defined once, centrally, and versioned; every dashboard, query, and agent resolves against the same model.
2. Agent-native — an AI agent (exposed over MCP) is a first-class interface, not a chatbot tacked onto a dashboard.
3. Warehouse-native — data stays where it is (Trino/Iceberg, Snowflake, BigQuery, Postgres, DuckDB); bilab queries in place, no copies.

## Architecture

- Semantic layer: Cube Core (Apache-2.0) — metrics, multi-tenant security context, pre-aggregation caching, SQL/REST/GraphQL/MCP.
- Query acceleration: Cube pre-aggregations on ClickHouse or DuckDB.
- Backend: Python (FastAPI + SQLAlchemy + Pydantic).
- Frontend: React + TypeScript + ECharts + react-grid-layout.
- AuthN/AuthZ: Keycloak (OIDC/SAML) + OPA/Casbin; row-level security via the semantic layer.
- Agent: LangGraph orchestration, MCP tools over the semantic layer, BYOK via LiteLLM.
- Metadata: OpenMetadata integration.

## Status

Early stage. See the phased plan in `docs/` as it lands.

## License

Proprietary (private repository).
