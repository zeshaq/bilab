"""Cube (semantic layer) routes, now authenticated per user (Phase 3).

Every request runs AS THE PERSON who asked: the Keycloak token is verified, the
identity forwarded to Cube, and OPA's masking/row filters apply. The audit log
records the caller's identity.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from ..services import audit, cube_client
from ..services.auth import get_identity

router = APIRouter(prefix="/api", tags=["cube"])


class CubeQuery(BaseModel):
    query: dict


@router.get("/cubes")
def list_cubes(identity: dict = Depends(get_identity)):
    meta = cube_client.cube_meta(identity)
    return [
        {
            "name": c["name"],
            "title": c.get("title"),
            "description": c.get("description"),
            "measures": [m["name"] for m in c.get("measures", [])],
            "dimensions": [d["name"] for d in c.get("dimensions", [])],
        }
        for c in meta.get("cubes", [])
    ]


@router.post("/query")
def run_query(body: CubeQuery, request: Request, identity: dict = Depends(get_identity)):
    audit.record(
        "query",
        user=identity["user"],
        client=request.client.host if request.client else None,
    )
    try:
        result = cube_client.cube_load(body.query, identity)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"data": result.get("data", []), "annotation": result.get("annotation", {})}
