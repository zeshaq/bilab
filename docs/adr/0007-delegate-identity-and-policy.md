# ADR-0007: Delegate identity to Keycloak and policy to OPA

Status: Accepted

## Context

Phase 3 (governance) requires per-user row-level security through the semantic
layer: one security context for humans and agents, with masking and row filters
applied identically to every query regardless of which surface issued it.

The lab's Trino already enforces OPA masking and row filters per identity,
keyed on the Keycloak token's principal and groups. Rebuilding a second
identity/policy plane for bilab would duplicate that and diverge from it.

## Decision

bilab owns no identity store and no policy store. It delegates:

- Identity to Keycloak (the lab's `datalab` realm): the backend verifies the
  caller's Keycloak token (signature, issuer, audience) and extracts the
  principal + groups.
- Policy to OPA (the lab's policy, enforced at Trino): the token is passed
  through to Trino, so the same masking/row filters apply to bilab metrics as
  to the person's own SQL client.

bilab's Cube and backend faithfully forward the caller's identity (X-User /
X-User-Groups / X-User-Token). Cube's cache is keyed per person, so one
person's result is never served to another.

Phase 3 login uses the resource-owner password grant (an internal-tool
shortcut, the same grant the lab's own tooling uses). The full browser OIDC
redirect flow is the production path and slots in without changing the model.

## Consequences

Positive:
- The single security context holds end to end: frontend -> backend -> Cube ->
  Trino, with OPA masking/RLS applied once, at Trino, for humans and agents alike.
- No duplicated or diverging policy; bilab inherits the lab's access decisions.
- Verified: an analyst sees amounts masked (NULL) and bank schema refused; an
  engineer sees full amounts and bank schema.

Negative:
- bilab depends on the lab's Keycloak realm + OPA being present and correct
  (acceptable — bilab already treats the lab's Trino as its data source).
- Password-grant login is not the final production auth; the OIDC redirect flow
  is still to be added.

## Alternatives considered

- bilab-owned Keycloak realm + OPA: full clean-room, but requires recreating
  users, groups, and policies and wiring a second OPA into Trino — large effort
  and a second place for access decisions to drift.
- Trust the token without verifying it in the backend: simpler, but lets forged
  identities into the audit log; rejected (production-grade security is the
  point of this phase).
