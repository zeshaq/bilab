# Conventional Commits

Format: `type(scope): description`

## Types

| Type | When to use | Example |
|---|---|---|
| feat | New feature or capability | `feat(semantic): add revenue metric to sales cube` |
| fix | Bug fix | `fix(auth): enforce RLS on agent-initiated queries` |
| refactor | Restructure, no behavior change | `refactor(api): extract query builder into module` |
| docs | Documentation only | `docs(adr): record Cube semantic layer decision` |
| test | Adding or updating tests | `test(auth): add RLS integration tests` |
| ci | CI/CD configuration | `ci: add backend test job to pipeline` |
| chore | Maintenance, deps, tooling | `chore: upgrade pytest to 8.x` |
| perf | Performance improvement | `perf(cache): index pre-aggregation lookups` |
| style | Formatting only | `style: run ruff on backend/` |
| build | Build system or external deps | `build: add frontend Vite config` |
| revert | Reverts a previous commit | `revert: revert "feat(api): add x"` |

## Scope (optional)

Short identifier for the area: `semantic`, `api`, `auth`, `ui`, `agent`,
`infra`, `docs`.

## Breaking changes

Add `!` after the type, or a `BREAKING CHANGE:` footer:

```
feat(api)!: require bearer tokens on all endpoints

BREAKING CHANGE: endpoints now require a Bearer token instead of an API key.
```

## Linking issues

```
Closes #42     # closes the issue on merge
Fixes #42      # same effect
Refs #42       # references without closing
```
