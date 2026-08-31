"""Load the Day 1 fixture into Postgres. Idempotent."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import psycopg
from dotenv import load_dotenv

# Load from services/agent/.env — the single source of the connection string.
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / "services" / "agent" / ".env")

DB = os.environ.get("DATABASE_URL")
if not DB:
    sys.exit("DATABASE_URL is not set in services/agent/.env")

FIXTURE_PROJECT_ID = "11111111-1111-1111-1111-111111111111"
FIXTURE_USER_ID = "00000000-0000-0000-0000-000000000001"

SQL = """
insert into users (id, handle, display)
values (%s, 'elisabeth', 'Elisabeth')
on conflict (handle) do nothing;

insert into projects (id, name, outgoing_owner_id, status)
values (%s, 'Acme Redesign', %s, 'draft')
on conflict (id) do nothing;
"""

with psycopg.connect(DB) as conn, conn.cursor() as cur:
    cur.execute(SQL, (FIXTURE_USER_ID, FIXTURE_PROJECT_ID, FIXTURE_USER_ID))
    conn.commit()

print(f"seeded project {FIXTURE_PROJECT_ID}")
