# Architecture Decision Records

Decisions that shape bilab, recorded as they are made. Each ADR is immutable
once accepted (superseded by a later ADR, never edited in place).

## Index

| ADR | Decision | Status |
|---|---|---|
| [0001](0001-cube-as-semantic-layer.md) | Cube Core as the semantic layer | Accepted |
| [0002](0002-not-grafana-scene.md) | Not using Grafana Scene for the frontend | Accepted |
| [0003](0003-mcp-as-agent-interface.md) | MCP as the agent interface | Accepted |
| [0004](0004-warehouse-native.md) | Warehouse-native (no data copy) | Accepted |
| [0005](0005-backend-frontend-stack.md) | Python backend + TypeScript frontend monorepo | Accepted |

## Template

```
# ADR-NNNN: Title

Status: Proposed | Accepted | Superseded by ADR-NNNN

## Context
The problem and the forces in play.

## Decision
What we chose, in one or two sentences.

## Consequences
What this makes easier, harder, and more expensive. Good and bad.

## Alternatives considered
What we rejected and why.
```
