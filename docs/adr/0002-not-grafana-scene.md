# ADR-0002: Not using Grafana Scene for the frontend

Status: Accepted

## Context

We evaluated Grafana Scene, an Apache-2.0 framework for building dashboard
experiences (panels, layout, variables, time ranges, data source plugins). It
would save substantial canvas/grid/variable plumbing.

However, Scene is built around Grafana's DataSourceApi and DataFrame model:
query-per-panel, data source plugins, transformations. That model is
observability-shaped, not BI-shaped — there is no concept of a governed metric
or a central semantic layer.

bilab's wedge (ADR-0001, ADR-0003) requires the semantic layer to drive the UI:
panel config comes from governed metrics, not a per-panel query string against
a plugin. Adopting Scene would mean building the semantic layer separately and
then writing Grafana data source plugins to adapt it in — reimplementing
Grafana's interfaces to serve our own model.

## Decision

Do not use Grafana Scene. Build a thin frontend with React + TypeScript +
ECharts + react-grid-layout, where the semantic layer drives panel configuration.

## Consequences

Positive:
- The viz layer stays thin and the semantic layer remains the product.
- No Grafana-shaped dependency or data-model coupling.
- Full control over a BI (not observability) look and feel.

Negative:
- We own the canvas, variables, filters, and time-range plumbing that Scene
  would have provided. This is weeks of work, but it is the least
  differentiating part of the tool and worth owning to avoid the coupling.

## Alternatives considered

- Grafana Scene: rejected for the data-model coupling above.
- Grafana Scene + existing Postgres data source pointed at Cube's SQL API: a
  cheap shortcut, but the result looks like Grafana, not a BI tool, and locks
  the product into the Grafana ecosystem.
- A heavier BI framework (e.g., building on Superset): rejected — Superset's
  semantic layer is too weak, and we'd be fighting its data model the same way.
