# Overlap

Autonomous handoff agent for freelance project transitions.
Submission for the Agents for Humans Hackathon (Devpost, Sep 14 2026).

Full plan lives in [`docs/overlap-plan.md`](docs/overlap-plan.md).
Repo context for Claude Code lives in [`CLAUDE.md`](CLAUDE.md).

## Layout
```
apps/web/          Next.js 14 dashboard + live status page
services/agent/    Python 3.11 + FastAPI + Strands Agents SDK
infra/             schema.sql + AgentCore terraform
demo/              fixture seeds
docs/              plan + design notes
```

## Local setup (macOS)

Prereqs: Node 20+, npm 10+, Python 3.11+.

```bash
# 1. Web
cd apps/web
cp .env.example .env.local          # fill in Supabase values
npm install
npm run dev                          # http://localhost:3000

# 2. Agent
cd services/agent
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env                 # fill in Supabase + AWS values
uvicorn overlap.main:app --reload --port 8000

# 3. Verify Day 1 exit criteria
curl -X POST http://localhost:8000/handoff
# => {"project_id":"11111111-...","project_name":"Acme Redesign"}
```

## Deploy
- Web: Vercel, `apps/web` as root dir. Deploy when the dashboard is presentable (Day 5).
- Agent: local for now; App Runner or Bedrock AgentCore later.
