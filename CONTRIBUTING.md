# Contributing

Thanks for contributing to bilab. These rules keep the codebase coherent and
safe to change. Read [docs/development/principles.md](docs/development/principles.md)
first — it is the source of truth; this file is the quick summary.

## Before you start

1. Open an issue (or find an existing one) describing the change.
2. Sweep for duplicates — search open issues and PRs first.
3. For anything larger than a small fix, record the design decision as an ADR
   in `docs/adr/` if it affects architecture.

## Workflow

1. Branch from `main` (short-lived, one topic per branch).
2. Follow strict TDD: write the failing test first, watch it fail, then write
   the minimal code to pass.
3. Commit with Conventional Commits format.
4. Push and open a pull request using the PR template.
5. Get one approving review; keep CI green.
6. Squash-merge into `main`.

## Commit messages

```
type(scope): description
```

Types: feat, fix, refactor, docs, test, ci, chore, perf, style, build, revert.
See `docs/development/conventional-commits.md` for the full reference.

## Tests

- No production code without a failing test first.
- Run the full suite before pushing: `pytest tests/ -q` (backend).
- Never merge with failing checks.

## Security

- Secrets go in `.env` files (gitignored), never in code or commits.
- All data access resolves through one authorization path (semantic layer
  security context + OPA/Casbin). Do not add a second enforcement point.
- Audit-log every action that reads or changes data.

## Documentation

- New public APIs (endpoints, MCP tools, semantic conventions) are documented
  when they land.
- Architecture changes require an ADR.
- Update README/roadmap when the change affects them.

## Definition of done

Test first (watched it fail) -> green suite -> docs updated -> PR reviewed ->
CI green -> behavior verified against real data where applicable.
