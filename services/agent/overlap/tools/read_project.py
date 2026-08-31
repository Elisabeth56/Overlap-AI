"""Tool: read a project by id from Postgres."""
from __future__ import annotations

from strands import tool

from overlap.state.db import get_project


@tool
def read_project(project_id: str) -> dict:
    """Fetch a project by its uuid. Returns a dict with id, name, status."""
    row = get_project(project_id)
    if row is None:
        return {"error": f"project {project_id} not found"}
    # Coerce non-JSON types for the model.
    return {
        "id": str(row["id"]),
        "name": row["name"],
        "status": row["status"],
    }
