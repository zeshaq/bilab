"""Agent endpoint: run the LangGraph agent AS THE CALLER (Phase 4).

The caller's Keycloak token is passed to the agent, which executes MCP tools as
the person — so the agent's answer (and anything it builds) is governed by the
caller's clearance.
"""
import os
import sys

# monorepo: make the repo root importable so the `agent` package resolves.
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..services.auth import get_identity

router = APIRouter(prefix="/api", tags=["agent"])


class AskRequest(BaseModel):
    question: str


@router.post("/agent/ask")
async def ask_agent(body: AskRequest, identity: dict = Depends(get_identity)):
    from agent.agent import ask
    result = await ask(body.question, identity["token"])
    return {
        "question": body.question,
        "plan": [p[0] for p in result.get("plan", [])],
        "answer": result.get("answer"),
    }
