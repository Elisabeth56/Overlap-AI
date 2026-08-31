"""FastAPI entry — POST /handoff/{project_id} runs one agent tick."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from overlap.agent import run_hello
from overlap.config import settings

app = FastAPI(title="Overlap Agent", version="0.1.0")

# Wide-open CORS is fine for Day 1 (only fixture data).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"ok": True}


@app.post("/handoff/{project_id}")
def handoff(project_id: str):
    """Day 1: run one hello-world tick and return the project name."""
    try:
        return run_hello(project_id)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/handoff")
def handoff_default():
    """Convenience: run against the fixture project id."""
    return handoff(settings.fixture_project_id)
