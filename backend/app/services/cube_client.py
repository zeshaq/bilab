"""Thin client over bilab's Cube (semantic layer) REST API.

Phase 3: every call forwards the caller's identity (X-User, X-User-Groups,
X-User-Token) so Cube runs the query AS THE PERSON and the lab's OPA
masking/RLS applies (ADR-0007). The caller's Keycloak token is never logged.
"""
import json
import urllib.error
import urllib.request

from ..config import CUBE_URL


def _request(method, path, identity, body=None):
    headers = {
        "x-user": identity["user"],
        "x-user-token": identity["token"],
        "x-user-groups": ",".join(identity.get("groups") or []),
    }
    data = json.dumps(body).encode() if body is not None else None
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(CUBE_URL + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.load(r)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise RuntimeError(f"semantic layer {exc.code}: {detail[:300]}") from exc


def cube_meta(identity):
    return _request("GET", "/cubejs-api/v1/meta", identity)


def cube_load(query, identity):
    return _request("POST", "/cubejs-api/v1/load", identity, {"query": query})
