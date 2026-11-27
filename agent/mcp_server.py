"""bilab MCP server — the agent interface over the semantic layer (ADR-0003, ADR-0007).

Each tool runs AS THE PERSON who asked: the caller's Keycloak token (sent as the
MCP client's Authorization header) is forwarded to the bilab backend, which
verifies it and passes the identity through Cube to Trino — so OPA masking and
row filters apply to agent queries exactly as to a human. One security context
for humans and agents.

Tools:
  metrics_catalog — list the governed metrics (cubes, measures, dimensions).
  metrics_query   — run a Cube query as the caller.

Run:  .venv/bin/python -m agent.mcp_server   (streamable HTTP on 0.0.0.0:8002)
"""
import json
import os
import urllib.request

from mcp.server.fastmcp import Context, FastMCP

BACKEND = os.environ.get("BILAB_BACKEND_URL", "http://127.0.0.1:8001")
MCP_HOST = os.environ.get("BILAB_MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.environ.get("BILAB_MCP_PORT", "8002"))

mcp = FastMCP("bilab", stateless_http=True, json_response=True, host=MCP_HOST, port=MCP_PORT)


def _token(ctx: Context) -> str:
    h = ctx.request_context.request.headers
    auth = h.get("authorization") or h.get("Authorization") or ""
    if auth.startswith("Bearer "):
        return auth[7:]
    # fall back to the x-user-token style if a gateway sits in front later
    return h.get("x-user-token") or ""


def _backend(path, token, method="GET", body=None):
    headers = {}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(body).encode() if body is not None else None
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(BACKEND + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


@mcp.tool()
async def metrics_catalog(ctx: Context) -> str:
    """List the governed business metrics of bilab's semantic layer: cubes
    (Transactions, Branches) with their measures, dimensions, titles and
    descriptions. Use metrics_query for counts, totals and breakdowns instead of
    writing SQL by hand."""
    token = _token(ctx)
    if not token:
        return json.dumps({"error": "no caller token: connect with a Keycloak bearer token"})
    return json.dumps(_backend("/api/cubes", token))


@mcp.tool()
async def metrics_query(query: str, ctx: Context) -> str:
    """Run a query on the semantic layer AS THE PERSON who asked. `query` is a
    Cube JSON query string, for example
    '{"measures":["transactions.count"],"dimensions":["transactions.channel"]}'.
    Amount measures come back empty for people whose clearance is lower — say so
    instead of guessing."""
    token = _token(ctx)
    if not token:
        return json.dumps({"error": "no caller token: connect with a Keycloak bearer token"})
    q = json.loads(query)
    return json.dumps(_backend("/api/query", token, method="POST", body={"query": q}))


@mcp.tool()
async def create_chart(title: str, chart_type: str, query: str, ctx: Context) -> str:
    """Create a standalone chart (a governed layout over a Cube query). `query` is
    a JSON-encoded Cube query string. chart_type is one of bar, line, area, pie,
    number, table. Runs AS THE PERSON."""
    token = _token(ctx)
    if not token:
        return json.dumps({"error": "no caller token: connect with a Keycloak bearer token"})
    return json.dumps(_backend("/api/charts", token, method="POST",
                               body={"title": title, "chart_type": chart_type, "query": json.loads(query)}))


@mcp.tool()
async def build_dashboard(title: str, charts: str, ctx: Context) -> str:
    """Create a dashboard with the given charts. `charts` is a JSON-encoded list of
    {"title": "...", "chart_type": "bar|line|area|pie|number|table", "query":
    {"measures": [...], "dimensions": [...]}}. The data is NOT copied — each chart
    runs through the semantic layer as whoever VIEWS the dashboard, so every viewer
    sees their own permitted data. Runs AS THE PERSON."""
    token = _token(ctx)
    if not token:
        return json.dumps({"error": "no caller token: connect with a Keycloak bearer token"})
    return json.dumps(_backend("/api/dashboards", token, method="POST",
                               body={"title": title, "charts": json.loads(charts)}))


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
