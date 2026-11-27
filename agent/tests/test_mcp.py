"""bilab Phase 4 acceptance tests — the agent interface (MCP) over the semantic layer.

The MCP server must expose governed metrics AS THE PERSON who asked: the caller's
Keycloak token is forwarded to the backend, which verifies it and passes the
identity through Cube to Trino, so OPA masking/RLS applies to agent queries
exactly as to a human (ADR-0003, ADR-0007). The single security context for
humans and agents.

Expected: ayesha.analyst -> masked amounts; rahim.engineer -> full amounts.

Run (the MCP server must be running: `.venv/bin/python -m agent.mcp_server`):
  set -a && . /home/system/datalab/identity/.env && set +a
  .venv/bin/pytest agent/tests/test_mcp.py -v
"""

import asyncio
import json
import os
import urllib.parse
import urllib.request

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

MCP = os.environ.get("BILAB_MCP_URL", "http://127.0.0.1:8002/mcp")
KC = "http://localhost:8180/realms/datalab"


def pw_token(user, pw):
    d = urllib.parse.urlencode({
        "grant_type": "password",
        "client_id": "datalab-cli",
        "username": user,
        "password": pw,
    }).encode()
    return json.load(urllib.request.urlopen(
        urllib.request.Request(KC + "/protocol/openid-connect/token", data=d), timeout=30)
    )["access_token"]


AYE = pw_token("ayesha.analyst", os.environ["DL_USER_AYESHA_PASSWORD"])
RAH = pw_token("rahim.engineer", os.environ["DL_USER_RAHIM_PASSWORD"])


async def call(tok, name, args):
    headers = {"Authorization": "Bearer " + tok} if tok else {}
    async with streamablehttp_client(MCP, headers=headers) as (r, w, _):
        async with ClientSession(r, w) as sess:
            await sess.initialize()
            return (await sess.call_tool(name, args)).content[0].text


def test_metrics_catalog_lists_cubes():
    r = asyncio.run(call(AYE, "metrics_catalog", {}))
    assert "transactions" in r and "branches" in r


def test_metrics_query_analyst_masked():
    r = asyncio.run(call(AYE, "metrics_query", {"query": json.dumps({"measures": ["transactions.total_amount"]})}))
    d = json.loads(r)
    assert d["data"][0]["transactions.total_amount"] is None, \
        "an agent asking as an analyst must get masked amounts"


def test_metrics_query_engineer_full():
    r = asyncio.run(call(RAH, "metrics_query", {"query": json.dumps({"measures": ["transactions.total_amount"]})}))
    d = json.loads(r)
    assert float(d["data"][0]["transactions.total_amount"]) > 0, \
        "an agent asking as an engineer must get full amounts"


def test_metrics_query_no_token_refused():
    r = asyncio.run(call(None, "metrics_query", {"query": json.dumps({"measures": ["transactions.count"]})}))
    assert "no caller token" in r
