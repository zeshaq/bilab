"""bilab dashboard persistence acceptance tests.

Dashboards and charts persist in bilab's own Postgres (infra/). A dashboard is a
layout over GOVERNED queries — the RLS is enforced when the query RUNS, so a
shared dashboard renders each viewer's own permitted data. These tests use the
svc-dataops identity (full clearance).

Run (Postgres must be up: `cd infra && docker compose up -d`):
  set -a && . /home/system/datalab/dataops/.env && set +a
  .venv/bin/pytest backend/tests/test_dashboards.py -v
"""

import json
import os
import urllib.parse
import urllib.request

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)
KC = "http://localhost:8180/realms/datalab"


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


def test_dashboard_requires_auth():
    r = client.post("/api/dashboards", json={"title": "x", "charts": []})
    assert r.status_code == 401


def test_create_and_get_dashboard():
    charts = [{
        "title": "transactions by channel",
        "chart_type": "bar",
        "query": {"measures": ["transactions.count"], "dimensions": ["transactions.channel"]},
    }]
    r = client.post("/api/dashboards", json={"title": "Test dashboard", "charts": charts}, headers=_auth())
    assert r.status_code in (200, 201), r.text
    did = r.json()["id"]

    r2 = client.get(f"/api/dashboards/{did}", headers=_auth())
    assert r2.status_code == 200
    body = r2.json()
    assert body["title"] == "Test dashboard"
    assert len(body["charts"]) == 1
    assert body["charts"][0]["title"] == "transactions by channel"


def test_list_dashboards():
    r = client.get("/api/dashboards", headers=_auth())
    assert r.status_code == 200
    rows = r.json()
    assert rows and all("title" in d and "id" in d for d in rows)


def test_create_chart():
    r = client.post("/api/charts", json={
        "title": "total amount",
        "chart_type": "number",
        "query": {"measures": ["transactions.total_amount"]},
    }, headers=_auth())
    assert r.status_code in (200, 201), r.text
    assert r.json()["id"] is not None
