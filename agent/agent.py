"""bilab agent — a LangGraph agent over the semantic layer (Phase 4).

Multi-step: decide which governed metric answers the question, execute the MCP
tools AS THE PERSON, and answer. The planner is a SCRIPTED stand-in
(deterministic, no API cost — the same pattern the lab's step tests use).

BYOK: switching to a real model (LiteLLM/OpenRouter) is a config change — set
BILAB_LLM_BACKEND=litellm and provide the key; `_plan` is the swap point. The
agent itself never changes.
"""
import asyncio
import json
import os
from typing import TypedDict

from langgraph.graph import END, StateGraph
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP_URL = os.environ.get("BILAB_MCP_URL", "http://127.0.0.1:8002/mcp")


async def _call_tool(token: str, name: str, args: dict):
    headers = {"Authorization": "Bearer " + token}
    async with streamablehttp_client(MCP_URL, headers=headers) as (r, w, _):
        async with ClientSession(r, w) as sess:
            await sess.initialize()
            return json.loads((await sess.call_tool(name, args)).content[0].text)


def _plan(question: str) -> list:
    """Scripted planner: a question -> MCP tool calls. Swap for a real LLM here."""
    q = question.lower()
    if "amount" in q or "revenue" in q or "total" in q:
        return [("metrics_query", {"query": json.dumps({"measures": ["transactions.total_amount"]})})]
    if "channel" in q:
        return [("metrics_query", {"query": json.dumps({"measures": ["transactions.count"], "dimensions": ["transactions.channel"], "order": {"transactions.count": "desc"}})})]
    if "account" in q:
        return [("metrics_query", {"query": json.dumps({"measures": ["transactions.distinct_accounts"]})})]
    return [("metrics_catalog", {})]


class State(TypedDict, total=False):
    question: str
    token: str
    plan: list
    results: list
    answer: str


def _decide(state: State) -> dict:
    return {"plan": _plan(state["question"])}


async def _execute(state: State) -> dict:
    results = []
    for name, args in state["plan"]:
        results.append(await _call_tool(state["token"], name, args))
    return {"results": results}


def _fmt(v):
    try:
        return "BDT " + format(float(v), ",.2f")
    except (TypeError, ValueError):
        return str(v)


def _summarize(results):
    parts = []
    for r in results:
        rows = r.get("data") or []
        if not rows:
            continue
        first = rows[0]
        if "transactions.total_amount" in first:
            v = first["transactions.total_amount"]
            parts.append("total amount: " + ("masked (no clearance)" if v is None else _fmt(v)))
        elif "transactions.count" in first and "transactions.channel" in first:
            parts.append("transactions by channel: " + ", ".join(
                f"{row['transactions.channel']}={int(row['transactions.count']):,}" for row in rows[:6]))
        elif "transactions.distinct_accounts" in first:
            parts.append("distinct accounts: " + f"{int(first['transactions.distinct_accounts']):,}")
        elif "branches.count" in first:
            parts.append("branches: " + first["branches.count"])
    return "; ".join(parts) if parts else json.dumps(results)[:200]


def _answer(state: State) -> dict:
    return {"answer": _summarize(state["results"])}


_graph = StateGraph(State)
_graph.add_node("decide", _decide)
_graph.add_node("execute", _execute)
_graph.add_node("answer", _answer)
_graph.add_edge("decide", "execute")
_graph.add_edge("execute", "answer")
_graph.add_edge("answer", END)
_graph.set_entry_point("decide")
agent = _graph.compile()


async def ask(question: str, token: str) -> dict:
    """Run the agent: plan -> execute MCP tools -> answer, as the token's identity."""
    return await agent.ainvoke({"question": question, "token": token})
