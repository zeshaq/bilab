"""bilab Phase 4 acceptance tests — the agent answers with governed numbers.

The LangGraph agent plans a question, executes MCP tools AS THE PERSON, and
answers — so OPA masking/RLS applies to the agent's answer exactly as to a
human. The planner is a scripted stand-in (no API cost).

Run (MCP server on :8002 must be running):
  set -a && . /home/system/datalab/identity/.env && set +a
  .venv/bin/pytest agent/tests/test_agent.py -v
"""

import asyncio
import json
import os
import urllib.parse
import urllib.request

from agent.agent import ask

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


def test_agent_answers_channel_breakdown():
    r = asyncio.run(ask("how many transactions by channel?", RAH))
    assert "transactions by channel" in r["answer"]
    assert "POS=" in r["answer"]


def test_agent_amount_masked_for_analyst():
    r = asyncio.run(ask("what is the total amount?", AYE))
    assert "masked" in r["answer"], "the agent must not reveal amounts to an analyst"


def test_agent_amount_full_for_engineer():
    r = asyncio.run(ask("what is the total amount?", RAH))
    assert "total amount: BDT" in r["answer"] and "masked" not in r["answer"]
