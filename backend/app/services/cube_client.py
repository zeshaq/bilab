"""Thin client over bilab's Cube (semantic layer) REST API."""
import json
import urllib.request

from ..config import CUBE_URL


def cube_meta():
    with urllib.request.urlopen(f"{CUBE_URL}/cubejs-api/v1/meta", timeout=30) as r:
        return json.load(r)


def cube_load(query):
    body = json.dumps({"query": query}).encode()
    req = urllib.request.Request(
        f"{CUBE_URL}/cubejs-api/v1/load",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)
