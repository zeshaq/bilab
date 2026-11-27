"""bilab API."""
from fastapi import FastAPI

from .routers import cube

app = FastAPI(title="bilab", version="0.1.0")
app.include_router(cube.router)


@app.get("/health")
def health():
    return {"status": "ok"}
