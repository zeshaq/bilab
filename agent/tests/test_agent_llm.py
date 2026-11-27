"""Opt-in BYOK acceptance test — runs the agent with a real LLM (DeepSeek).

NOT part of the default (free) suite: it spends API money, so it is skipped
unless DEEPSEEK_API_KEY is set. Run it explicitly:

  export DEEPSEEK_API_KEY=...   # or read it from the key file
  set -a && . /home/system/datalab/identity/.env && set +a
  .venv/bin/pytest agent/tests/test_agent_llm.py -v

The LLM only PLANS the tool calls; RLS is enforced downstream by the caller's
Keycloak token through Cube/Trino, so a masked analyst stays masked no matter
which model planned the query.
"""

import asyncio
import json
import os
import urllib.parse
import urllib.request

import pytest

from agent.agent import ask

pytestmark = pytest.mark.skipif(
    not os.environ.get("DEEPSEEK_API_KEY"),
    reason="set DEEPSEEK_API_KEY to run the BYOK test (spends API money)",
)

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


def test_llm_plans_and_respects_rls():
    a = asyncio.run(ask("what is the total amount?", AYE))
    assert "masked" in a["answer"], "the real model must not reveal amounts to an analyst"
    e = asyncio.run(ask("what is the total amount?", RAH))
    assert "BDT" in e["answer"] and "masked" not in e["answer"]


def test_llm_plans_channel_and_catalog():
    r = asyncio.run(ask("how many transactions per channel?", RAH))
    assert "POS=" in r["answer"]
    r2 = asyncio.run(ask("what metrics do we have?", RAH))
    assert "transactions" in r2["answer"] and "branches" in r2["answer"]
