# Overlap — repo context for Claude Code

> This file is auto-loaded by Claude Code in every session. Keep it compressed. Full plan lives at `docs/overlap-plan.md`.

## What we're building

**Overlap** — an autonomous handoff agent for freelance project transitions. Submission for the Agents for Humans Hackathon on Devpost (cutoff Sep 14, 2026; internal ship date Sep 6).

The theme requires: *"runs autonomously and only surfaces when there's a real decision to make."* Everything below serves that constraint.

## Stack

- **Frontend:** Next.js 14 (app router) + TypeScript + TailwindCSS on Vercel
- **Backend:** Python 3.11 + FastAPI + Strands Agents SDK
- **LLM:** Anthropic Claude via Amazon Bedrock
- **Runtime:** Bedrock AgentCore (bonus) with an App Runner + Postgres-job-cursor fallback
- **State:** Supabase Postgres — the ONLY source of truth

## Repo layout

```
overlap/
  apps/web/                 Next.js dashboard + live status page
  services/agent/
    overlap/
      agent.py              top-level Strands agent + loop
      tools/                one file per tool
      state/                Postgres accessors
      prompts/              agent prompts as .md files
  infra/schema.sql          source-of-truth schema (see docs/overlap-plan.md §4)
  infra/bedrock.tf          AgentCore deployment (bonus)
  demo/seed.py              loads the fixture project into Postgres
  docs/overlap-plan.md      the full 7-day plan — read this before proposing scope
```

## Behavior contract (do not violate)

- The agent is **stateless between ticks.** All memory lives in Postgres.
- On each tick, the agent:
  1. reads project + inventory + open threads
  2. picks the highest-priority unresolved item
  3. picks a strategy: `contact_outgoing | self_serve_from_log | verify_credential | brief_incoming | escalate`
  4. executes **one** action
  5. writes an `events` row and any state changes
- The agent surfaces to the human freelancer only via the `decisions` table.
- Terminal state: every `inventory_items` row with `criticality >= 2` is in state `verified` or `acknowledged`.
- `events` is append-only. Never update it.
- Every strategy switch writes `attempts.next_action` explaining the reason — this is what makes the demo legible.

## Source-of-truth tables

`projects · inventory_items · threads · attempts · decisions · events`

Full schema in `infra/schema.sql`. Field-level detail in `docs/overlap-plan.md §4`.

## What NOT to build

Unless the plan explicitly says otherwise for the current day:
- No real integrations (Slack, GitHub, email — all mocked; mocks write to `events` so the UI is honest)
- No auth (hardcode a demo user in `middleware.ts`)
- No multi-project support (seed one)
- No decision logic beyond what's needed for the demo path
- No UI polish beyond the design system in `docs/overlap-plan.md §5` (day 5 work)

## The demo path (the only path that must work)

1. Freelancer clicks "hand off Acme project"
2. Agent inventories: 3 credentials · 4 tickets · 3 promises · 2 head-only decisions
3. Emails outgoing for `POSTGRES_URL` → ignored
4. Switches strategy → extracts from CI log → verifies with `\dt`
5. Asks outgoing only the *decision* the log can't recover ("why Bun over Node?")
6. Drafts incoming's briefing tailored to their Postgres version
7. Incoming acks 4/7 → agent sends pointed follow-ups on the risky 3
8. One decision surfaces to freelancer: "Close ticket #241? Client silent 6 days"
9. HANDOFF COMPLETE

If a change breaks this path, revert it.

## Deadlines

- **Ship** · Sat 5 Sep 2026 (Africa/Lagos)
- **Submit** · Sun 6 Sep 2026
- **Devpost cutoff** · Sep 14, 17:00 PDT (8-day buffer preserved)

## When in doubt

Read `docs/overlap-plan.md` for the day-by-day slice, exit criteria, and cut list. That doc is the source of truth for scope decisions.
