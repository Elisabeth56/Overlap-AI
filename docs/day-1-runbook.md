# Day 1 runbook — commands you run on macOS

Everything below runs in **Terminal on your Mac** (not the Cowork VM).
The VM can't reach Supabase or AWS, so dev servers live natively.

## 0. Prereqs (skip any you already have)
```bash
# Node + pnpm
node --version        # want v20+; if missing, `brew install node@20`
corepack enable && corepack prepare pnpm@9 --activate
pnpm --version

# Python 3.11
python3.11 --version  # if missing, `brew install python@3.11`
```

## 1. Apply the schema
Open your Supabase project → **SQL Editor** → New query.
Paste the contents of `infra/schema.sql`, click **Run**. Then repeat for `demo/seed.sql`.
(One curl-friendly path is possible with `psql`, but the SQL Editor is faster and avoids installing another client.)

Verify in **Table Editor**: you should see 7 tables, and `projects` has one row named "Acme Redesign".

## 2. Wire env files
```bash
cd ~/Documents/Overlap\ AI

# Web
cp apps/web/.env.example apps/web/.env.local
# Edit apps/web/.env.local:
#   NEXT_PUBLIC_SUPABASE_URL       (Project Settings > API)
#   NEXT_PUBLIC_SUPABASE_ANON_KEY  (same page, "anon public")

# Agent
cp services/agent/.env.example services/agent/.env
# Edit services/agent/.env:
#   DATABASE_URL  (Settings > Database > Connection string > URI, session pooler)
#   AWS_* left blank for Day 1
```

## 3. Boot the agent
```bash
cd services/agent
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn overlap.main:app --reload --port 8000
```

Verify (in a second terminal):
```bash
curl -X POST http://localhost:8000/handoff
# => {"project_id":"11111111-...","project_name":"Acme Redesign"}
```

## 4. Boot the web
```bash
cd apps/web
pnpm install
pnpm dev
```

Open http://localhost:3000 — it redirects to `/projects/11111111-1111-1111-1111-111111111111`.
You should see "Realtime: connected" and "No events yet."

## 5. Prove Realtime is live
Curl the agent once more — the event feed on the page should get a new row
within a second, no refresh needed:
```bash
curl -X POST http://localhost:8000/handoff
```

## 6. Deploy web to Vercel (no CLI needed)
1. https://vercel.com/new → import `Elisabeth56/Overlap-AI`
2. **Root directory:** `apps/web`
3. **Framework preset:** Next.js (auto)
4. **Environment variables:** paste `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `NEXT_PUBLIC_FIXTURE_PROJECT_ID` (all three)
5. Deploy. Copy the auto-generated URL back to me — I'll pin it in CLAUDE.md.

Domain is deferred to Day 5/6 per the plan.

## Day 1 exit criteria — check all four
- [ ] `curl -X POST http://localhost:8000/handoff` returns `{"project_name": "Acme Redesign"}`
- [ ] The Vercel URL loads and shows the empty event feed
- [ ] A fresh `curl` populates the feed in real time
- [ ] `git status` is clean, everything committed and pushed
