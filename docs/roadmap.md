# Roadmap

Phased build plan. Each phase ends with something runnable and verified against
real data in the lab (Trino/Iceberg over Oracle CDC).

## Phase 0 — Foundation (current)

Documentation and engineering standards in place before any code.

- [x] Repo created, private
- [x] Architecture, ADRs, product vision
- [x] Engineering principles, contribution guide
- [x] Issue/PR templates, CI scaffold, repo hygiene

## Phase 1 — Semantic core (2-4 weeks)

Goal: a governed metric model on real lab data, queryable over SQL/REST/MCP.

- [ ] Stand up Cube Core against Trino (Iceberg tables from Oracle CDC)
- [ ] Define initial metric model (dimensions, measures, joins) for a real domain
- [ ] Row-level security via security context
- [ ] Pre-aggregation caching (DuckDB/ClickHouse)
- [ ] Verify: query a metric via SQL, REST, GraphQL, and MCP; same numbers everywhere

## Phase 2 — Viz MVP (3-6 weeks)

Goal: dashboards and Explore on top of the semantic layer.

- [ ] FastAPI backend: API surface, auth scaffolding, audit log
- [ ] React + ECharts + react-grid-layout frontend
- [ ] 8-10 chart types done well (line, bar, area, scatter, table, big number,
      pie, funnel, heatmap, map)
- [ ] Filters, time-grain, drill-down, dashboard persistence (Postgres)
- [ ] Verify: build a dashboard from the semantic layer end to end

## Phase 3 — Governance (2-4 weeks)

Goal: production-grade security.

- [ ] Keycloak (OIDC/SAML/LDAP)
- [ ] OPA/Casbin fine-grained authorization
- [ ] RLS through the semantic layer (single security context for humans + agents)
- [ ] Audit log for every action
- [ ] Verify: two users with different RLS see different data, incl. via agent

## Phase 4 — Agent (2-4 weeks)

Goal: the agent-native wedge is real, not marketing.

- [ ] MCP server over the semantic layer (list_metrics, run_query, create_chart,
      build_dashboard, schedule_report)
- [ ] LangGraph multi-step agent
- [ ] BYOK via LiteLLM/OpenRouter
- [ ] Verify: "show me revenue by region, add it to the Q3 dashboard" end to end

## Phase 5 — Enterprise features (months)

- [ ] Scheduling and alerts (Celery)
- [ ] Embedded SDK (iframe + JWT)
- [ ] Collaboration (comments, sharing)
- [ ] Dashboards-as-code (git import/export, versioning)
- [ ] Caching at scale, multi-tenancy
- [ ] SSO/SAML, SCIM, audit logging maturity

## Definition of done

Every phase: code merged via PR, tests passing in CI, and the "Verify" line
demonstrated against real lab data — never just container status.
