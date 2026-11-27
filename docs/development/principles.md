# Engineering Principles

These are the rules for how bilab is built. They exist so that a year from now
the codebase is still coherent, testable, and safe to change. Violating one
requires an explicit, documented exception — not a silent shortcut.

## 1. Test-Driven Development (non-negotiable)

No production code without a failing test first.

- RED: write the test, watch it fail.
- GREEN: write the minimal code to pass.
- REFACTOR: clean up, keep tests green.

Tests after code prove nothing — they pass immediately and don't catch the bug
they were written for. If a test passes on first run, it isn't testing new
behavior; fix the test.

- Every new function/method has a test.
- Tests describe behavior, not implementation.
- Use real code, not mocks, unless a mock is unavoidable (external services).
- Edge cases and error paths are covered.

Test commands (Phase 2 onward):

```
pytest tests/ -q          # backend
```

## 2. Conventional Commits

Every commit message follows the Conventional Commits format:

```
type(scope): description
```

Types: feat, fix, refactor, docs, test, ci, chore, perf, style, build, revert.

Examples:
- `feat(semantic): add revenue metric to sales cube`
- `fix(auth): enforce RLS on agent-initiated queries`
- `docs(adr): record decision to use Cube as semantic layer`

See the full reference in `docs/development/conventional-commits.md`.

## 3. Trunk-based development

- `main` is always releasable — it builds, tests pass, and it runs.
- All work happens on short-lived branches, merged via pull request.
- No direct commits to `main`. No long-lived feature branches.
- Squash or rebase merge; keep history linear and readable.

## 4. Pull requests and review

- Every change is a PR. No exceptions for "small" fixes.
- PRs use the pull request template (summary, motivation, changes, test plan).
- At least one approving review before merge.
- Review is for correctness, security, and behavior — not style nitpicks
  (automation handles style).
- Never merge with failing checks. Verify CI yourself, don't trust a badge.

## 5. Security

- Secrets live in `.env` files (gitignored), never in code, config, or commits.
- Every data access — human or agent — resolves through one authorization path
  (semantic layer security context + OPA/Casbin). There is no second path.
- Row-level security is enforced in one place. Never add a second enforcement
  point that can drift.
- Audit-log every action that reads or changes data.

## 6. Documentation

- Architecture decisions are ADRs in `docs/adr/` — one per decision, with
  context and rejected alternatives.
- New public APIs (backend endpoints, MCP tools, semantic model conventions)
  are documented when they land, not after.
- README and roadmap stay current; they are part of the definition of done.

## 7. Definition of done

A change is done only when all of these are true:

- [ ] Test written first, watched it fail, then pass
- [ ] Full test suite green
- [ ] No warnings or errors in test output
- [ ] Docs updated where the change affects them
- [ ] PR reviewed and CI green
- [ ] Behavior verified against real data (not just unit tests) where applicable
