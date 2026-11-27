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

## Phase 3 — Governance (done)

Goal: production-grade security.

- [x] Keycloak — reused the lab's realm as the identity plane (ADR-0007)
- [x] OPA — reused the lab's policy, enforced at Trino; no bilab-owned policy
- [x] RLS through the semantic layer: Cube + backend pass the caller's Keycloak
      token through; OPA masking/row filters apply per identity
- [x] Per-user audit log (backend records the caller's identity)
- [x] Verify: analyst sees masked amounts + refused bank schema; engineer sees
      full amounts + bank schema (6/6 governance tests + live end-to-end curl)
- [ ] Full browser OIDC redirect flow (Phase 3 uses the password grant; the
      OIDC flow is the production path)

## Phase 4 — Agent (done, core)

Goal: the agent-native wedge is real, not marketing.

- [x] MCP server over the semantic layer: metrics_catalog + metrics_query,
      running AS THE PERSON (forwards the caller's Keycloak token to the backend)
- [x] LangGraph multi-step agent (decide -> execute -> answer) driving the MCP tools
- [x] Verify: the agent answers with governed numbers — analyst gets "masked",
      engineer gets the full amount + breakdowns (7/7 agent+MCP tests green)
- [ ] BYOK via LiteLLM/OpenRouter — scaffolded (scripted planner stand-in, config
      swap documented); a real model is not exercised to avoid API cost
- [ ] create_chart / build_dashboard / schedule_report tools — need dashboard
      persistence (Phase 2 remainder / Phase 5)

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
