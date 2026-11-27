# ADR-0006: Clean-room semantic layer + Phase 1 service identity

Status: Accepted

## Context

When Phase 1 (semantic core) began, the datalab already had a working Cube
semantic layer (its "Step 19"): Cube on Trino/Iceberg via Polaris, with
per-user Keycloak passthrough, OPA masking/RLS, cubestore caching, and an MCP
data server. bilab could have built on it, or built its own.

## Decision

bilab builds its own clean-room semantic layer: its own Cube deployment and
metric models in the bilab repo (`semantic/`), pointing at the lab's Trino as a
data source. The lab stays a data source and reference; bilab owns its models,
config, and tests.

Phase 1 connects as a single governed service identity (Keycloak client
`svc-dataops`), fetched per query via `semantic/token.js`. Per-user token
passthrough and RLS move to Phase 3 (governance).

## Consequences

Positive:
- bilab's models and tests live in bilab's repo and evolve independently of the
  lab's Step 19.
- A single governed identity keeps Phase 1 simple while still exercising OPA's
  masking/row filters (the identity's own clearance applies to every metric).
- Proved the roadmap's core claim end to end: metric == plain SQL on the same
  table, via REST and GraphQL.

Negative:
- bilab runs a second Cube beside the lab's — accepted duplication for
  clean-room ownership; the lab's Step 19 remains the richer reference.
- One identity only: Phase 1 does not yet demonstrate per-user RLS (Phase 3).

## Alternatives considered

- Build on the lab's Step 19 (extract its models/config): faster, but couples
  bilab's semantic layer to the lab's repo and gateway.
- Test the existing lab Cube only: proves the concept but leaves bilab with no
  semantic layer of its own.
