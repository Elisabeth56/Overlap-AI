"""Postgres accessors. All agent state lives here."""
from __future__ import annotations

import psycopg
from psycopg.rows import dict_row

from overlap.config import settings


def _connect():
    # Short-lived connections keep the agent stateless between ticks.
    return psycopg.connect(settings.database_url, row_factory=dict_row)


def get_project(project_id: str) -> dict | None:
    """Return the project row as a dict, or None if not found."""
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(
            "select id, name, status, outgoing_owner_id, incoming_owner_id, "
            "client_ref, deadline, created_at from projects where id = %s",
            (project_id,),
        )
        return cur.fetchone()


def emit_event(project_id: str, kind: str, actor: str, payload: dict | None = None) -> None:
    """Append one row to events. Never updates."""
    with _connect() as conn, conn.cursor() as cur:
        cur.execute(
            "insert into events (project_id, kind, actor, payload) values (%s, %s, %s, %s)",
            (project_id, kind, actor, psycopg.types.json.Json(payload or {})),
        )
        conn.commit()
