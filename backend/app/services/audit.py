"""Minimal append-only audit log (Phase 2 scaffolding).

Proper audit (Postgres + retention + per-user identity) lands in Phase 3/5,
where every action — human or agent — is recorded with the caller's identity.
"""
import json
import threading
import time

from ..config import AUDIT_LOG

_lock = threading.Lock()


def record(event, **fields):
    entry = {"ts": time.time(), "event": event, **fields}
    with _lock:
        with open(AUDIT_LOG, "a") as f:
            f.write(json.dumps(entry) + "\n")


def read(limit=100):
    try:
        with open(AUDIT_LOG) as f:
            lines = f.readlines()
    except FileNotFoundError:
        return []
    return [json.loads(line) for line in lines[-limit:]]
