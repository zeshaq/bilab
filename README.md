# bilab

A semantic-layer-first, agent-native business intelligence tool.

bilab competes on three things commercial BI tools bolt on after the fact:

1. Semantic layer first — metrics are defined once, centrally, and versioned; every dashboard, query, and agent resolves against the same model.
2. Agent-native — an AI agent (exposed over MCP) is a first-class interface, not a chatbot tacked onto a dashboard.
3. Warehouse-native — data stays where it is (Trino/Iceberg, Snowflake, BigQuery, Postgres, DuckDB); bilab queries in place, no copies.

## Documentation

| Doc | What it covers |
|---|---|
| [docs/product/vision.md](docs/product/vision.md) | What bilab is, who it serves, how it competes |
| [docs/architecture.md](docs/architecture.md) | System architecture and component responsibilities |
| [docs/adr/](docs/adr/) | Architecture Decision Records — why key choices were made |
| [docs/roadmap.md](docs/roadmap.md) | Phased build plan |
| [docs/development/principles.md](docs/development/principles.md) | Engineering standards: TDD, commits, review, branching |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |

## Repository layout

```
backend/    Python (FastAPI) service — API, query orchestration, auth, agent
frontend/   React + TypeScript — ECharts dashboards, Explore UI
semantic/   Cube Core semantic layer — metric models, pre-aggregations
infra/      Docker Compose, Keycloak, OPA, deployment configs
docs/       Product, architecture, ADRs, development standards
```

## Status

Pre-implementation. Documentation and engineering standards are in place;
Phase 1 (semantic core) is next. See [docs/roadmap.md](docs/roadmap.md).

## License

Source-available, all rights reserved. See [LICENSE](LICENSE).
