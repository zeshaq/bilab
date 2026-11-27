# Product Vision

## What bilab is

A business intelligence tool where the governed semantic layer — not the
dashboard — is the product. Metrics are defined once, centrally, and versioned;
dashboards, ad-hoc analysis, and AI agents all resolve against the same model.

## Problem

Commercial BI tools have three structural weaknesses that a new tool can exploit:

1. Weak or absent semantic layers. Looker is the exception; most tools (Power BI,
   Tableau, Superset) let metric logic drift across charts and dashboards. When
   "revenue" means different things in different reports, users stop trusting
   the numbers.
2. AI bolted on, not built in. Copilots and "ask your data" features are
   chatbots layered on top of dashboards. They are not grounded in a governed
   model, so they hallucinate metrics and don't inherit security.
3. Copy-everything architectures. ETL-based tools move data into their own
   store, adding cost, latency, and a second place for data to go stale.

## Wedge

bilab competes on three things, in priority order:

1. Semantic layer first. Governed, versioned metrics are the product. Everything
   else renders them.
2. Agent-native. The agent is a first-class interface over the same governed
   model — not a demo feature. It is exposed over MCP so it works wherever the
   user already is (Slack, chat, IDE, embedded).
3. Warehouse-native. Query in place, no copy. bilab is a layer over the data
   the customer already owns.

## Who it serves

- Data teams: a single governed place to define metrics, with dashboards and
  agents as free outputs.
- Business users: answer questions in plain language and get governed numbers
  without knowing SQL or table structures.
- Product/embedded: embed governed analytics inside a customer's own product.

## Non-goals (initially)

- Replacing the warehouse. bilab never owns the data.
- Winning on breadth. 10 chart types done deeply, not 100 done shallowly.
- Observability/monitoring (logs, traces, alerting on infra). That is Grafana's
  domain; bilab is BI for business metrics.

## Positioning vs. incumbents

| | Power BI | Tableau | Looker | ThoughtSpot | bilab |
|---|---|---|---|---|---|
| Semantic layer | weak | weak | strong (LookML) | medium | strong (core) |
| Agent-native | bolted on | bolted on | bolted on | strong | strong (core) |
| Warehouse-native | partial | partial | yes | yes | yes |
| Open (MCP) | no | partial | partial | partial | yes |
| Pricing | AI tier upsell | AI tier upsell | cloud anchor | per-seat | BYOK, no AI tax |
