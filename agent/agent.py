"""bilab agent — a LangGraph agent over the semantic layer (Phase 4).

Multi-step: decide which governed metric answers the question, execute the MCP
tools AS THE PERSON, and answer.

The planner is a deterministic stand-in by default (free, no API cost). When
DEEPSEEK_API_KEY is set, the agent uses a real model (DeepSeek chat,
OpenAI-compatible) to plan the tool calls. The model only PLANS; RLS is enforced
downstream by the caller's Keycloak token through Cube/Trino, so a masked
analyst stays masked no matter which model planned the query.
"""
import asyncio
import json
import os
import re
import urllib.request
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


DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

_TOOL_HINT = (
    "Available tools: metrics_catalog (list governed metrics) and metrics_query "
    "(run a Cube query AS THE PERSON). Known measures: transactions.count, "
    "transactions.total_amount, transactions.distinct_accounts, branches.count. "
    "Known dimensions: transactions.channel, transactions.txn_type, "
    "transactions.direction, transactions.customer_segment, transactions.currency, "
    "transactions.txn_time."
)


def _plan_scripted(question: str) -> list:
    """Deterministic stand-in planner (no API cost — used when no LLM key is set)."""
    q = question.lower()
    if "amount" in q or "revenue" in q or "total" in q:
        return [("metrics_query", {"query": json.dumps({"measures": ["transactions.total_amount"]})})]
    if "channel" in q:
        return [("metrics_query", {"query": json.dumps({"measures": ["transactions.count"], "dimensions": ["transactions.channel"], "order": {"transactions.count": "desc"}})})]
    if "account" in q:
        return [("metrics_query", {"query": json.dumps({"measures": ["transactions.distinct_accounts"]})})]
    return [("metrics_catalog", {})]


def _parse_calls(content: str) -> list:
    """Parse the LLM's tool-call JSON into [(tool, args), ...], tolerating fences
    and object-vs-array wrapping."""
    content = content.strip()
    if content.startswith("```"):
        content = content.strip("`").strip()
        if content.lower().startswith("json"):
            content = content[4:].strip()
    try:
        obj = json.loads(content)
    except json.JSONDecodeError:
        m = re.search(r"\[.*\]|\{.*\}", content, re.DOTALL)
        if not m:
            raise
        obj = json.loads(m.group(0))
    if isinstance(obj, dict):
        obj = obj.get("calls") or obj.get("tools") or []
    if isinstance(obj, dict):
        obj = [obj]
    out = []
    for c in obj:
        args = c.get("args") or {}
        if isinstance(args.get("query"), dict):
            args = dict(args)
            args["query"] = json.dumps(args["query"])
        out.append((c["tool"], args))
    return out


def _plan_llm(question: str) -> list:
    """Real-model planner (BYOK): ask DeepSeek to plan the tool calls."""
    key = os.environ["DEEPSEEK_API_KEY"]
    system = (
        "You plan queries for a governed BI semantic layer. "
        + _TOOL_HINT
        + ' Respond with ONLY a JSON object: {"calls":[{"tool":"metrics_query",'
          '"args":{"query":"{\\"measures\\":[\\"transactions.count\\"]}"}}]}. '
          "args.query is a JSON-encoded Cube query string. Choose metrics_query when the "
          "question names a metric; choose metrics_catalog only when it asks what metrics exist."
    )
    body = json.dumps({
        "model": DEEPSEEK_MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": question}],
        "temperature": 0,
    }).encode()
    req = urllib.request.Request(
        DEEPSEEK_BASE_URL.rstrip("/") + "/chat/completions",
        data=body,
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    return _parse_calls(data["choices"][0]["message"]["content"])


def _plan(question: str) -> list:
    """Pick the planner: a real LLM (BYOK) when DEEPSEEK_API_KEY is set, else the
    scripted stand-in."""
    if os.environ.get("DEEPSEEK_API_KEY"):
        return _plan_llm(question)
    return _plan_scripted(question)


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
        if isinstance(r, list):
            # metrics_catalog returns a list of cubes
            names = [c["name"] for c in r if isinstance(c, dict) and c.get("name")]
            if names:
                parts.append("metrics available: " + ", ".join(names))
            continue
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
