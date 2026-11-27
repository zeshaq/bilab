"""bilab backend acceptance tests — the API surface over the semantic layer.

These are integration tests: the FastAPI app is exercised in-process with
TestClient, and the Cube client talks to bilab's real Cube (127.0.0.1:4199),
so a query here returns live governed numbers. Since Phase 3, requests must
carry a valid Keycloak token; these tests use the svc-dataops service identity
(which has full clearance) to verify the proxy is faithful.

Run from the repo root (env: dataops/.env for the svc-dataops secret):
  set -a && . /home/system/datalab/dataops/.env && set +a
  .venv/bin/pytest backend/tests/test_api.py -v
"""

import json
import os
import urllib.parse
import urllib.request

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
CUBE = os.environ.get("BILAB_CUBE_URL", "http://127.0.0.1:4199")
KC = "http://localhost:8180/realms/datalab"
SVC_USER = "service-account-svc-dataops"


def _svc_token():
    d = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": "svc-dataops",
        "client_secret": os.environ["DATAOPS_OIDC_CLIENT_SECRET"],
    }).encode()
    return json.load(urllib.request.urlopen(
        urllib.request.Request(KC + "/protocol/openid-connect/token", data=d), timeout=30)
    )["access_token"]


def _auth():
    return {"Authorization": "Bearer " + _svc_token()}


def _cube_load(query):
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        CUBE + "/cubejs-api/v1/load",
        data=body,
        headers={
            "Content-Type": "application/json",
            "x-user": SVC_USER,
            "x-user-token": _svc_token(),
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_list_cubes():
    r = client.get("/api/cubes", headers=_auth())
    assert r.status_code == 200
    names = {c["name"] for c in r.json()}
    assert {"transactions", "branches"} <= names
    assert all(c.get("title") and c.get("description") for c in r.json())


def test_query_matches_direct_cube():
    query = {"measures": ["transactions.count"], "dimensions": ["transactions.channel"]}
    r = client.post("/api/query", json={"query": query}, headers=_auth())
    assert r.status_code == 200
    got = r.json()["data"]

    want = _cube_load(query)["data"]
    got_map = {row["transactions.channel"]: int(row["transactions.count"]) for row in got}
    want_map = {row["transactions.channel"]: int(row["transactions.count"]) for row in want}
    # Live data grows between the two queries, so compare channels exactly and
    # counts within a small tolerance (the proxy is faithful, not frozen).
    assert set(got_map) == set(want_map)
    for channel, n in want_map.items():
        assert abs(got_map[channel] - n) <= max(50, n * 0.01), f"{channel}: backend={got_map[channel]} cube={n}"


def test_query_returns_real_numbers():
    r = client.post("/api/query", json={"query": {"measures": ["transactions.total_amount"]}}, headers=_auth())
    assert r.status_code == 200
    data = r.json()["data"]
    assert data and data[0]["transactions.total_amount"] is not None
    assert float(data[0]["transactions.total_amount"]) > 0


def test_query_is_audited():
    r = client.post("/api/query", json={"query": {"measures": ["branches.count"]}}, headers=_auth())
    assert r.status_code == 200
    from app.services import audit
    entries = audit.read(limit=20)
    assert any(e["event"] == "query" for e in entries)
