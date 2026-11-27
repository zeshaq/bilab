"""bilab API."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import auth, cube

app = FastAPI(title="bilab", version="0.1.0")

# Phase 2/3 dev: allow the Vite dev server to call the backend directly.
# Tightened to the real origin(s) when auth+deployment land (Phase 3/5).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(cube.router)


@app.get("/health")
def health():
    return {"status": "ok"}
