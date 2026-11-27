# Roadmap

Phased build plan. Each phase ends with something runnable and verified against
real data in the lab (Trino/Iceberg over Oracle CDC).

## Phase 0 — Foundation (current)

Documentation and engineering standards in place before any code.

- [x] Repo created, private
- [x] Architecture, ADRs, product vision
- [x] Engineering principles, contribution guide
- [x] Issue/PR templates, CI scaffold, repo hygiene

## Phase 1 — Semantic core (done)

Goal: a governed metric model on real lab data, queryable over SQL/REST/GraphQL.

- [x] Stand up Cube Core against Trino (Iceberg tables from Oracle CDC) — bilab's
      own Cube (bilab-cube :4199) + Cubestore on datalab-net; lab Trino is the data source
- [x] Define initial metric model (transactions, branches) on
      lakehouse.curated.txn_enriched and lakehouse.bank.branches
- [x] Pre-aggregation caching (Cubestore)
- [x] Verify: metric == plain SQL on the same table, via REST and GraphQL
      (5/5 acceptance tests green; total_amount, distinct_accounts, counts all agree)
- [ ] Row-level security via security context — deferred to Phase 3 (Phase 1 uses
      a single governed identity, svc-dataops)
- [ ] MCP surface — deferred to Phase 4 (the agent layer)

## Phase 2 — Viz MVP (in progress)

Goal: dashboards and Explore on top of the semantic layer.

- [x] FastAPI backend: API surface (/api/cubes, /api/query), audit log scaffold
- [x] React + ECharts frontend: dashboard (KPI cards + bar charts) + Explore
- [x] Verify: dashboard renders governed numbers end to end (browser-verified:
      KPIs + charts from the live semantic layer)
- [ ] More chart types (line, area, scatter, pie, funnel, heatmap, map, table) —
      bar + big-number cards done
- [ ] Filters, time-grain, drill-down
- [ ] Dashboard persistence (Postgres)
- [ ] Auth scaffolding — deferred to Phase 3

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
