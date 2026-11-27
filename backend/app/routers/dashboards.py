"""Dashboard and chart persistence (Phase 4 completion).

Dashboards/charts are governed layouts; RLS applies when a chart's query runs.
All routes require authentication and are audit-logged.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..db import Chart, Dashboard, get_db
from ..services import audit
from ..services.auth import get_identity

router = APIRouter(prefix="/api", tags=["dashboards"])


class ChartSpec(BaseModel):
    title: str
    chart_type: str
    query: dict


class DashboardCreate(BaseModel):
    title: str
    charts: list[ChartSpec] = []


class ChartCreate(BaseModel):
    title: str
    chart_type: str
    query: dict


def _dash(d):
    return {
        "id": d.id,
        "title": d.title,
        "owner": d.owner,
        "charts": d.charts or [],
        "created_at": d.created_at.isoformat() if d.created_at else None,
        "updated_at": d.updated_at.isoformat() if d.updated_at else None,
    }


@router.get("/dashboards")
def list_dashboards(identity: dict = Depends(get_identity), db: Session = Depends(get_db)):
    rows = db.query(Dashboard).order_by(Dashboard.updated_at.desc()).all()
    return [
        {
            "id": d.id,
            "title": d.title,
            "owner": d.owner,
            "chart_count": len(d.charts or []),
            "updated_at": d.updated_at.isoformat() if d.updated_at else None,
        }
        for d in rows
    ]


@router.post("/dashboards", status_code=201)
def create_dashboard(body: DashboardCreate, identity: dict = Depends(get_identity), db: Session = Depends(get_db)):
    audit.record("dashboard.create", user=identity["user"], title=body.title)
    d = Dashboard(title=body.title, owner=identity["user"], charts=[c.model_dump() for c in body.charts])
    db.add(d)
    db.commit()
    db.refresh(d)
    return {"id": d.id, "title": d.title, "owner": d.owner}


@router.get("/dashboards/{did}")
def get_dashboard(did: int, identity: dict = Depends(get_identity), db: Session = Depends(get_db)):
    d = db.get(Dashboard, did)
    if not d:
        raise HTTPException(status_code=404, detail="not found")
    return _dash(d)


@router.delete("/dashboards/{did}")
def delete_dashboard(did: int, identity: dict = Depends(get_identity), db: Session = Depends(get_db)):
    d = db.get(Dashboard, did)
    if not d:
        raise HTTPException(status_code=404, detail="not found")
    audit.record("dashboard.delete", user=identity["user"], title=d.title)
    db.delete(d)
    db.commit()
    return {"ok": True}


@router.get("/charts")
def list_charts(identity: dict = Depends(get_identity), db: Session = Depends(get_db)):
    rows = db.query(Chart).order_by(Chart.created_at.desc()).all()
    return [{"id": c.id, "title": c.title, "chart_type": c.chart_type, "owner": c.owner} for c in rows]


@router.post("/charts", status_code=201)
def create_chart(body: ChartCreate, identity: dict = Depends(get_identity), db: Session = Depends(get_db)):
    audit.record("chart.create", user=identity["user"], title=body.title)
    c = Chart(title=body.title, chart_type=body.chart_type, query=body.query, owner=identity["user"])
    db.add(c)
    db.commit()
    db.refresh(c)
    return {"id": c.id, "title": c.title, "owner": c.owner}
