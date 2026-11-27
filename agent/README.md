# agent/

bilab's agent interface (Phase 4) — the agent-native wedge (ADR-0003, ADR-0007).

## What's here

- `mcp_server.py` — MCP server (streamable HTTP on :8002) exposing
  `metrics_catalog` and `metrics_query`. Each tool runs AS THE PERSON: the
  caller's Keycloak token is forwarded to the backend, so OPA masking/RLS applies
  to agent queries exactly as to a human.
- `agent.py` — a LangGraph agent (decide -> execute -> answer) that drives the
  MCP tools. The planner is a scripted stand-in (deterministic, no API cost).
- `tests/` — acceptance tests for the MCP server and the agent (7 tests).

## Run

```bash
# MCP server (streamable HTTP):
.venv/bin/python -m agent.mcp_server   # 0.0.0.0:8002

# Tests (MCP server must be running):
set -a && . /home/system/datalab/identity/.env && set +a
.venv/bin/pytest agent/tests/ -v
```

## BYOK

The planner (`_plan` in `agent.py`) is a deterministic stand-in, the same
pattern the lab's step tests use so tests never spend API money. To use a real
model, set `BILAB_LLM_BACKEND=litellm` and provide the key; `_plan` is the swap
point — the graph and the MCP tools do not change.

## Not yet built

`create_chart`, `build_dashboard` and `schedule_report` tools need dashboard
persistence (Postgres), which is still open (Phase 2 remainder / Phase 5). The
MCP server currently exposes the read path (metrics_catalog, metrics_query).
