# ADR-0001: Cube Core as the semantic layer

Status: Accepted

## Context

bilab's core claim is that metrics are defined once, centrally, and versioned,
and that dashboards, ad-hoc analysis, and AI agents all resolve against the same
model. This is the weak point of most BI tools (including Superset, which has
no strong governed metric layer), and it is the main place where an agent can
hallucinate numbers if not grounded in a governed model.

We needed a semantic layer that provides: metric/dimension/join definitions,
row-level security via a per-request security context, pre-aggregation caching,
and multiple query interfaces (SQL, REST, GraphQL) plus MCP for agents.

## Decision

Use Cube Core (Apache-2.0) as the semantic layer.

## Consequences

Positive:
- Ships a mature, battle-tested semantic engine rather than building one.
- Pre-aggregation caching is built in, giving "instant dashboard" performance
  without a custom cache layer.
- Multi-tenant security context gives one place to enforce RLS for humans and
  agents alike.
- Exposes the model over SQL (Postgres-compatible), REST, GraphQL, and MCP —
  the agent interface (ADR-0003) comes largely for free.
- Open source; no lock-in; can be self-hosted in the lab.

Negative:
- Cube Core is Node.js, while the rest of the backend is Python (ADR-0005).
  This is an accepted polyglot cost at the engine layer.
- Cube's modeling is code/CLI-driven, which is fine for a governed model but
  means metric definitions aren't edited in a GUI.

## Alternatives considered

- dbt + MetricFlow: strong for transformation and metric definition, but
  MetricFlow is oriented to dbt's workflow and doesn't provide the serving
  layer, caching, or MCP out of the box. Would need to build the runtime.
- Malloy: elegant semantic query language, but a language/toolkit rather than a
  serving runtime; more work to build caching, security, and serving on top.
- Build our own: full control, but a semantic layer is years of work and the
  single highest-risk component. Rejected as premature.
- Superset's virtual datasets/saved metrics: too weak for a governed,
  versionable, centrally-defined model (see ADR-0002's sibling context).
