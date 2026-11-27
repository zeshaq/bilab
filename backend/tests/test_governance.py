"""bilab Phase 3 acceptance tests — governance (RLS through the semantic layer).

The backend must authenticate the caller (Keycloak bearer token), pass that
identity through Cube to Trino, and let the lab's OPA masking/row-filters apply
per identity — the single security context for humans and agents (ADR-0007).

Expected, from the lab's access policy:
  ayesha.analyst  (analysts)       -> amounts masked (NULL), bank schema refused
  rahim.engineer  (data-engineers) -> full amounts, bank schema readable

Run from the repo root (env: identity/.env for the demo user passwords):
  set -a && . /home/system/datalab/identity/.env && set +a
  .venv/bin/pytest backend/tests/test_governance.py -v
"""

import json
import os
import urllib.parse
import urllib.request

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
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


def q(tok, query):
    headers = {"Authorization": "Bearer " + tok} if tok else {}
    return client.post("/api/query", json={"query": query}, headers=headers)


def test_no_token_returns_401():
    r = q(None, {"measures": ["transactions.count"]})
    assert r.status_code == 401


def test_analyst_amounts_masked():
    r = q(AYE, {"measures": ["transactions.total_amount"], "dimensions": ["transactions.channel"]})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data and all(row["transactions.total_amount"] is None for row in data), \
        "analyst must see amounts masked (NULL)"


def test_engineer_amounts_visible():
    r = q(RAH, {"measures": ["transactions.total_amount"], "dimensions": ["transactions.channel"]})
    assert r.status_code == 200
    data = r.json()["data"]
    assert data and all(
        row["transactions.total_amount"] is not None and float(row["transactions.total_amount"]) > 0
        for row in data
    ), "engineer must see full amounts"


def test_analyst_branches_refused():
    r = q(AYE, {"measures": ["branches.count"]})
    # refused schema surfaces as a semantic-layer error (not a clean 28)
    assert not (r.status_code == 200 and r.json().get("data") == [{"branches.count": "28"}]), \
        "analyst must not read the bank schema"


def test_engineer_branches_works():
    r = q(RAH, {"measures": ["branches.count"]})
    assert r.status_code == 200
    assert r.json()["data"][0]["branches.count"] == "28"


def test_audit_records_identity():
    q(RAH, {"measures": ["transactions.count"]})
    from app.services import audit
    entries = audit.read(limit=50)
    assert any(e.get("user") == "rahim.engineer" for e in entries), \
        "the audit log must record the caller's identity"
