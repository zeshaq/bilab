"""bilab's own state store: dashboards and charts (Postgres, see infra/).

A dashboard is a layout over GOVERNED queries — the data is never copied here;
each chart's query runs through the semantic layer as the viewer, so RLS applies
at render time. Owner is recorded for audit.
"""
from sqlalchemy import Column, DateTime, Integer, String, create_engine, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import DATABASE_URL

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class Dashboard(Base):
    __tablename__ = "dashboards"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    owner = Column(String, nullable=False)
    charts = Column(JSONB, nullable=False, default=lambda: [])
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)


class Chart(Base):
    __tablename__ = "charts"

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    chart_type = Column(String, nullable=False)
    query = Column(JSONB, nullable=False)
    owner = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)


def init_db():
    Base.metadata.create_all(engine)


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
