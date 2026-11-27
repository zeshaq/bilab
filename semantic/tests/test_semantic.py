"""bilab Phase 1 acceptance tests — the semantic layer.

Prove the core claim of the roadmap: a governed metric and the equivalent plain
SQL on the same table return the same numbers ("same numbers everywhere").

These are integration tests: they run bilab's Cube (REST API on 127.0.0.1:4199)
and the lab's Trino (https://localhost:8087) as the SAME governed identity
(svc-dataops), then compare. Live data grows between the two queries, so
comparisons allow a small relative tolerance.

Environment (the lab is the data source, so a few lab values are needed):
  DATAOPS_OIDC_CLIENT_SECRET  svc-dataops Keycloak client secret (lab dataops/.env)
  BILAB_CUBE_URL              default http://127.0.0.1:4199
  BILAB_TRINO_URL             default https://localhost:8087
  TRINO_CA                    default the lab's trino/tls/trino.crt

Run from the repo root:
  set -a && . /home/system/datalab/dataops/.env && set +a
  python -m pytest semantic/tests/test_semantic.py -v
"""

import json
import os
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request

import pytest

CUBE = os.environ.get("BILAB_CUBE_URL", "http://127.0.0.1:4199")
TRINO = os.environ.get("BILAB_TRINO_URL", "https://localhost:8087").rstrip("/")
KC = "http://localhost:8180/realms/datalab"
CA = os.environ.get("TRINO_CA", "/home/system/datalab/trino/tls/trino.crt")

CTX = ssl.create_default_context(cafile=CA)
SECRET = os.environ.get("DATAOPS_OIDC_CLIENT_SECRET", "")


def _svc_token():
    d = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": "svc-dataops",
        "client_secret": SECRET,
    }).encode()
    return json.load(urllib.request.urlopen(
        urllib.request.Request(KC + "/protocol/openid-connect/token", data=d), timeout=30)
    )["access_token"]


def _trino(sql):
    """Run one SQL statement on Trino as svc-dataops; return {"columns": [...], "rows": [[...]]}."""
    tok = _svc_token()
    h = {"Authorization": "Bearer " + tok, "X-Trino-User": "service-account-svc-dataops",
         "X-Trino-Source": "bilab-tests"}
    r = json.load(urllib.request.urlopen(
        urllib.request.Request(TRINO + "/v1/statement", data=sql.encode(), headers=h), context=CTX, timeout=120))
    cols, rows = None, []
    while True:
        cols = r.get("columns", cols)
        rows += r.get("data", [])
        if "error" in r:
            raise RuntimeError(r["error"].get("message", "")[:300])
        if "nextUri" not in r:
            break
        time.sleep(0.2)
        r = json.load(urllib.request.urlopen(
            urllib.request.Request(r["nextUri"], headers=h), context=CTX, timeout=120))
    return {"columns": [c["name"] for c in cols or []], "rows": rows}


def _cube_get(path):
    with urllib.request.urlopen(CUBE + path, timeout=120) as r:
        return json.load(r)


def _cube_load(query):
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(CUBE + "/cubejs-api/v1/load", data=body,
                                 headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


def _close(a, b, tolerance):
    return abs(a - b) <= max(tolerance, abs(b) * 0.01)


# --- the metric model is served --------------------------------------------------------------------------

def test_meta_lists_bilab_cubes():
    meta = _cube_get("/cubejs-api/v1/meta")
    names = {c["name"] for c in meta.get("cubes", [])}
    assert {"transactions", "branches"} <= names
    tx = next(c for c in meta["cubes"] if c["name"] == "transactions")
    assert tx.get("description")
    assert any(m.get("description") for m in tx["measures"])


# --- a metric agrees with plain SQL on the same table -----------------------------------------------------

def test_transaction_count_by_channel_matches_sql():
    cube = _cube_load({
        "measures": ["transactions.count"],
        "dimensions": ["transactions.channel"],
        "order": {"transactions.count": "desc"},
    })
    got = {row["transactions.channel"]: row["transactions.count"] for row in cube["data"]}
    direct = _trino("select channel, count(*) as n from lakehouse.curated.txn_enriched group by channel")
    want = {row[0]: row[1] for row in direct["rows"]}
    assert got and want
    assert set(got) == set(want)
    for channel, n in want.items():
        assert _close(int(got[channel]), n, 50), f"{channel}: cube={got[channel]} sql={n}"


def test_total_amount_matches_sql():
    cube = _cube_load({"measures": ["transactions.total_amount"]})
    got = cube["data"][0]["transactions.total_amount"]
    direct = _trino("select sum(amount) from lakehouse.curated.txn_enriched")
    want = direct["rows"][0][0]
    # If the governed identity sees amounts masked, both are empty — still consistent.
    if got is None and want is None:
        return
    assert got is not None and want is not None, f"cube={got} sql={want} (masking divergence)"
    assert _close(float(got), float(want), 1000), f"cube={got} sql={want}"


def test_distinct_accounts_matches_sql():
    cube = _cube_load({"measures": ["transactions.distinct_accounts"]})
    got = cube["data"][0]["transactions.distinct_accounts"]
    direct = _trino("select count(distinct account_id) from lakehouse.curated.txn_enriched")
    want = direct["rows"][0][0]
    assert _close(int(got), int(want), 50), f"cube={got} sql={want}"


def test_branches_count_matches_sql():
    cube = _cube_load({"measures": ["branches.count"]})
    got = cube["data"][0]["branches.count"]
    direct = _trino("select count(*) from lakehouse.bank.branches")
    want = direct["rows"][0][0]
    assert int(got) == int(want), f"cube={got} sql={want}"
