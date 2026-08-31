# Day 1 runbook — commands on macOS

Everything runs natively (VM has no egress to Supabase/AWS).

## 0. Prereqs
```bash
node --version         # want 20+; `brew install node@20` if missing
python3.11 --version   # `brew install python@3.11` if missing
```

## 1. Apply the schema
Supabase → SQL Editor → paste `infra/schema.sql` → Run.

Verify in Table Editor: 7 tables exist.

## 2. Boot the agent + seed the fixture
```bash
cd services/agent
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
python ../../demo/seed.py         # inserts the Acme Redesign fixture
uvicorn overlap.main:app --reload --port 8000
```

Verify (second terminal):
```bash
curl -X POST http://localhost:8000/handoff/11111111-1111-1111-1111-111111111111
# => {"project_id":"11111111-...","project_name":"Acme Redesign"}
```

If the connection fails, swap `DATABASE_URL` in `services/agent/.env` for the **Session pooler** URI (host `aws-0-<region>.pooler.supabase.com`) and retry.

## 3. Boot the web
```bash
cd apps/web
npm install
npm run dev
```

Open http://localhost:3000 — redirects to the fixture project page.
You should see "Realtime: connected" and "No events yet."

## 4. Prove Realtime works
Leave the browser tab open. Curl the agent:
```bash
curl -X POST http://localhost:8000/handoff/11111111-1111-1111-1111-111111111111
```
The event feed populates within a second, **no refresh** — that's the pipe validated end-to-end (agent → Postgres → Realtime → browser).

## Day 1 exit
- [ ] Schema applied, 7 tables in Supabase
- [ ] `curl` returns the project name
- [ ] Realtime shows "connected", curl makes a live row appear
- [ ] `git push origin main`

## Deferred
- Vercel deploy → Day 5 (when the dashboard is presentable)
- Bedrock model invocation → Day 2 (uncomment block in `overlap/agent.py`)
- Custom domain → Day 5/6
