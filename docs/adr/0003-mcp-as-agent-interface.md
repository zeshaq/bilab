# ADR-0003: MCP as the agent interface

Status: Accepted

## Context

bilab's second wedge is being agent-native: an AI agent is a first-class
interface, not a chatbot bolted onto dashboards. The agent must be grounded in
the governed semantic layer and must inherit the same security context as human
users — otherwise it hallucinates metrics or leaks data.

The practical problem: how does an external AI client (Claude, Cursor, our own
chatbot, a customer's agent) interact with bilab safely?

## Decision

Expose bilab's capabilities over the Model Context Protocol (MCP) — a set of
tools (list_metrics, run_query, create_chart, build_dashboard,
schedule_report) that wrap the semantic layer. Both external MCP clients and
bilab's built-in agent use the same tools.

## Consequences

Positive:
- Open, standard interface; no proprietary lock-in for customers or ourselves.
- One set of tools serves every agent surface (built-in chatbot, external
  clients, embedded agents), so capabilities and permission checks are written
  once.
- Every tool call resolves through the same RBAC/RLS as the web UI, so agents
  inherit the security posture by construction.
- The semantic layer (ADR-0001) already offers MCP, giving a large head start.

Negative:
- MCP tool design requires care: too coarse and agents can't reason, too fine
  and they thrash. This is a design cost, not a correctness cost.
- We commit to keeping the tool surface stable and versioned, like an API.

## Alternatives considered

- Custom REST-only agent API: more control but bespoke, and every AI client
  needs custom integration. MCP is already the de facto standard for agent-tool
  connectivity.
- Text-to-SQL directly against the warehouse (no semantic layer): rejected —
  ungoverned SQL is exactly how agents hallucinate metrics and bypass security.
