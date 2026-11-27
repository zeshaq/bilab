"""Interactive chat with the bilab agent (runs AS YOU).

Usage:
    .venv/bin/python -m agent.chat [username]

The agent queries the semantic layer through the MCP tools AS YOU (your Keycloak
token), so OPA masking/RLS applies — an analyst sees masked amounts, an engineer
sees full numbers. With DEEPSEEK_API_KEY set, a real model plans the queries;
otherwise the deterministic stand-in planner is used.

Prerequisites: the backend (:8001) and the MCP server (:8002) running.
"""
import asyncio
import getpass
import json
import os
import sys
import urllib.request

from .agent import ask

BACKEND = os.environ.get("BILAB_BACKEND_URL", "http://127.0.0.1:8001")


def login(username, password):
    body = json.dumps({"username": username, "password": password}).encode()
    req = urllib.request.Request(BACKEND + "/api/login", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["token"]


async def main():
    username = sys.argv[1] if len(sys.argv) > 1 else input("username: ")
    password = os.environ.get("BILAB_PASSWORD") or getpass.getpass("password: ")
    try:
        token = login(username, password)
    except Exception as e:
        print("login failed:", e)
        return
    print(f"signed in as {username}. Ask about the data, or type 'quit'.")
    while True:
        try:
            q = input("\n> ")
        except EOFError:
            break
        q = q.strip()
        if not q:
            continue
        if q.lower() in ("quit", "exit"):
            break
        try:
            r = await ask(q, token)
        except Exception as e:
            print("error:", e)
            continue
        print(r["answer"])


if __name__ == "__main__":
    asyncio.run(main())
