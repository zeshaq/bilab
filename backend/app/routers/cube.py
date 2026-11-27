"""Cube (semantic layer) routes.

Phase 2: a thin, faithful proxy over the semantic layer, with an audit trail.
Phase 3 adds authentication/authorization (Keycloak + OPA) in front of these —
the router is written so an auth dependency can slot in without reshaping it.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from ..services import audit, cube_client

router = APIRouter(prefix="/api", tags=["cube"])


class CubeQuery(BaseModel):
    query: dict


@router.get("/cubes")
def list_cubes():
    meta = cube_client.cube_meta()
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
def run_query(body: CubeQuery, request: Request):
    audit.record("query", client=request.client.host if request.client else None)
    try:
        result = cube_client.cube_load(body.query)
    except Exception as exc:  # surface the semantic layer's error to the caller
        raise HTTPException(status_code=502, detail=f"semantic layer error: {exc}") from exc
    return {"data": result.get("data", []), "annotation": result.get("annotation", {})}
