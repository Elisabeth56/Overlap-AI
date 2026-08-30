# Overlap — 7-Day Sprint Plan

> The handoff period, run by an agent. Seven days from empty repo to a submitted Devpost.

**Start** · Sun 30 Aug 2026
**Ship** · Sat 5 Sep 2026
**Submit** · Sun 6 Sep 2026
**Devpost cutoff** · Sep 14, 17:00 PDT · 8-day buffer

---

## §01 · North star

A freelancer marks a project handing off. The agent inventories what's in the outgoing dev's head, chases what only they can give, self-serves what a log can reveal, briefs the incoming dev in their vocabulary, waits for real acknowledgement, and only surfaces to the freelancer when a decision needs a human. Terminal state: *handoff complete* — verified, not just declared.

**Judged on five equal criteria:** Technical implementation on Strands Agents SDK · Design of the full product experience · Impact against a specific real problem · Creativity (non-obvious use of the SDK) · Presentation. A blog post adds up to 0.6 bonus. Bedrock AgentCore deployment strengthens the technical score; not required.

Every day below ends with a working slice on the demo path. If a day slips, the cut list at the bottom names what to drop before scope creeps sideways.

---

## §02 · The seven days

Seven working days, one shipped slice each. Days are dated in Africa/Lagos. Submit on Day 7, keep the 8-day buffer for the video edit, a rewrite of the Devpost story, or a scoped integration if the base is stable.

### Day 1 · Sun 30 Aug · Scope lock & foundations
*Nothing is on rails yet — today is the rails.*

**Deliverables**
- GitHub repo `overlap` with the layout in §5
- AWS account with Bedrock model access (Claude on Bedrock)
- Supabase project + `schema.sql` applied
- Strands "hello world" that reads a project row and prints its name
- Next.js app on Vercel with a single `/projects/[id]` route rendering an empty event feed
- Domain registered (`useoverlap.com` or the winner)

**Do not build**
- Any real integration (Slack, GitHub, email)
- Auth, billing, multi-project
- Agent logic beyond a print
- UI polish beyond default Tailwind

**Exit:** `curl`ing a FastAPI endpoint invokes the Strands agent, which reads a fixture project from Postgres and returns its name. The web page shows a placeholder event feed connected to Supabase Realtime.

---

### Day 2 · Mon 31 Aug · Inventory phase
*The agent learns what's on the outgoing dev's plate.*

**Deliverables**
- Fixture: one seeded project with mock GitHub issues, credential list, Slack thread digest, Stripe subscription list
- Tool: `read_project_state()` returning the fixture as a structured payload
- Agent step: classify each item into `inventory_items` with a kind and criticality
- Event emission: every write to `inventory_items` also writes an `events` row

**Prompt work**
- Draft the inventory-classifier system prompt in `prompts/inventory.md`
- Evaluate on the fixture: expect exactly 12 items, 3 criticality-3

**Exit:** Triggering "hand off" on the fixture project streams inventory items into the web event feed within ~15 seconds. Every item is auditable in Postgres.

---

### Day 3 · Tue 1 Sep · Chase-outgoing loop
*The most Strands-heavy day. Build the adaptation loop.*

**Deliverables**
- Tools: `email_send()` (mock — logs to Postgres), `check_replies()` (fixture-polled), `extract_from_ci_log()`
- Agent loop: for each unresolved criticality-3 item, pick a strategy, act, wait, adapt
- Strategies: `contact_outgoing`, `self_serve_from_log`, `verify_credential`, `escalate`
- Persist `attempts` + `threads` with strategy change reasons

**The decision gate**
- Write to `decisions` only when the agent has exhausted strategies and needs the human
- Web UI: a single decision chip in the header — click to resolve
- Resolution rewakes the agent

**Exit:** Demo path 1 works end-to-end — agent emails outgoing dev for a credential, fixture reply never arrives, agent switches to CI-log extraction, verifies, moves on.

---

### Day 4 · Wed 2 Sep · Onboard-incoming loop
*Close the three-party loop. This is the wedge.*

**Deliverables**
- Tool: `brief_incoming(item, incoming_profile)` — tailored to their stack
- Agent step: draft briefing, request ack, parse response, follow up on ambiguous acks
- Terminal-state detector: every criticality ≥ 2 item is `verified` or `acknowledged`

**Durability**
- Wrap the agent invocation as a Bedrock AgentCore session (bonus — attempt only if Day 3 shipped clean)
- Fallback: FastAPI background task with a Postgres-backed job queue

**Exit:** On the fixture, "hand off" runs unattended for ~2 minutes and reaches `status = complete` with a clean event log.

---

### Day 5 · Thu 3 Sep · Dashboard & live status page
*The video sells this. The UI is the video.*

**Deliverables**
- Project setup screen: pick project, pick outgoing, pick incoming, "hand off"
- Live status: three columns (inventory, outgoing, incoming) with items animating between states
- Decision surface: a single amber chip at the top when the agent needs the human
- Event log at the bottom, streaming from Supabase Realtime

**Design**
- Match the visual identity of the plan doc — same palette, same typography — so the brand reads consistent
- Reduced-motion respected on the state animations

**Exit:** Recording a screen capture of the full demo path produces a video with visible drama at three moments: agent adapting, decision chip, complete state.

---

### Day 6 · Fri 4 Sep · Rehearse, cut, record
*Ship the demo. Cut anything that fights the take.*

**Deliverables**
- Three dry runs of the 90-second demo
- Screen recording + voiceover
- Five screenshots for Devpost gallery
- Cut anything from the cut list that isn't stable

**Buffer use**
- If Days 1-5 shipped clean: attempt one real integration (Slack webhook is safest)
- If not: keep everything mocked and polish the UI

**Exit:** A final `.mp4` is on disk. The dashboard is deployed. The demo project seeds fresh in under 10 seconds.

---

### Day 7 · Sat 5 Sep · Story, submit, blog
*Words are 40% of the score. Write them like they are.*

**Deliverables**
- Devpost writeup: problem, mechanism, "aha" moment, tech stack, what's built, what's next
- Blog post for the bonus 0.6 points — "Building an autonomous handoff agent on Strands" — one technical arc + one code excerpt
- README with a 30-second install and a demo GIF
- Submit on Devpost. Don't wait for Day 14.

**Framing**
- Position against XMPro's briefing-only handover: *Overlap owns the loop, not the artifact*
- Pitch the three-party wedge — most agent demos own a single-actor loop; this holds context across outgoing, incoming, and absent client

**Exit:** Submission confirmation email in inbox. Devpost page renders correctly. Blog post live. Whatever happens after this is buffer.

---

## §03 · Architecture

The agent is stateless between ticks. Everything it knows lives in Postgres — the only source of truth. Bedrock AgentCore (or a FastAPI background loop as fallback) owns durability; the agent's job on each tick is to read the current state, choose one action, and write back. This is what makes the "runs autonomously in the background" theme survive judges' second look — you can restart the process mid-handoff and lose nothing.

```
                         ┌───────────────────────┐
                         │      FREELANCER       │
                         │ source of intent      │
                         │ target of decisions   │
                         └────────────┬──────────┘
                                      │ intent
              ┌───────────────────────┼───────────────────────┐
              ▼                                               ▼
   ┌─────────────────────┐                        ┌─────────────────────┐
   │  NEXT.JS DASHBOARD  │◀────── POST /handoff ──│   FASTAPI CONTROL   │
   │  Vercel             │                        │  AWS App Runner     │
   │  setup · status ·   │                        │  POST /handoff      │
   │  decision chip      │                        │  GET  /project/:id  │
   └──────────┬──────────┘                        └──────────┬──────────┘
              │ Realtime subscribe                            │ invoke
              │                                               ▼
              │                              ┌──────────────────────────────┐
              │                              │   STRANDS AGENT LOOP         │
              │                              │   Bedrock AgentCore          │
              │                              │   Claude on Bedrock          │
              │                              │   stateless between ticks    │
              │                              │   read · pick · act · write  │
              │                              └────────┬──────────┬──────────┘
              │                                       │ tool_use │ read/write
              │                                       ▼          │
              │        ┌──────────────────────────────────────┐  │
              │        │ TOOLS                                │  │
              │        │ email_send · check_replies           │  │
              │        │ ci_log_extract · verify_secret       │  │
              │        │ brief_incoming · github              │  │
              │        └──────────────────────────────────────┘  │
              │                                                  │
              ▼                                                  ▼
   ┌──────────────────────────────────────────────────────────────────────┐
   │  POSTGRES — SOURCE OF TRUTH                                          │
   │  projects · inventory_items · threads · attempts · decisions · events│
   └──────────────────────────────────────────────────────────────────────┘
```

**Three loops, one state machine.** The agent's life is three phases that write into the same tables: *inventory* discovers items, *chase-outgoing* resolves items that need the departing dev, *onboard-incoming* transfers items to the arriving dev. A project's `status` column is the phase marker; the agent picks the next action by reading the current phase plus the state of the highest-priority open item.

---

## §04 · Source of truth (schema)

Six tables. Everything else is derived. Every state transition also writes to `events` — that's what the dashboard streams and what the demo video shows filling in. Keep `events` append-only; never update it.

```sql
-- source of truth for the Overlap handoff agent

create table projects (
  id                 uuid primary key default gen_random_uuid(),
  name               text not null,
  outgoing_owner_id  uuid not null,
  incoming_owner_id  uuid,
  client_ref         jsonb,
  status             text not null check (status in
    ('draft','inventorying','chasing_outgoing',
     'onboarding_incoming','verifying','complete','abandoned')),
  deadline           timestamptz,
  created_at         timestamptz default now()
);

create table inventory_items (
  id            uuid primary key default gen_random_uuid(),
  project_id    uuid references projects(id) on delete cascade,
  kind          text not null check (kind in
    ('credential','ticket','decision','relationship','infra','commitment')),
  label         text not null,
  external_ref  jsonb,
  state         text not null check (state in
    ('unknown','discovered','gathered','verified','acknowledged','failed')),
  criticality   int  not null default 1,   -- 1=nice, 2=needed, 3=blocking
  created_at    timestamptz default now(),
  resolved_at   timestamptz
);

create table threads (
  id               uuid primary key default gen_random_uuid(),
  project_id       uuid references projects(id) on delete cascade,
  actor            text not null check (actor in ('outgoing','incoming','client')),
  channel          text not null check (channel in ('email','slack','sms')),
  subject          text,
  purpose          text not null,          -- "recover POSTGRES_URL"
  linked_item_id   uuid references inventory_items(id),
  status           text not null check (status in
    ('open','awaiting_reply','stalled','resolved','abandoned')),
  strategy         text,                    -- current strategy the agent is trying
  last_activity_at timestamptz
);

create table attempts (
  id             uuid primary key default gen_random_uuid(),
  thread_id      uuid references threads(id) on delete cascade,
  strategy       text not null,
  sent_at        timestamptz not null,
  message_body   text,
  reply_at       timestamptz,
  reply_summary  text,
  outcome        text check (outcome in
    ('answered','ignored','partial','refused','error')),
  next_action    text                       -- the reason the strategy changes
);

create table decisions (                    -- the "surfaces only for real decisions" gate
  id           uuid primary key default gen_random_uuid(),
  project_id   uuid references projects(id) on delete cascade,
  question     text not null,
  options      jsonb,
  raised_at    timestamptz default now(),
  resolved_at  timestamptz,
  resolved_by  uuid,
  resolution   jsonb
);

create table events (                       -- append-only audit + status feed
  id          bigserial primary key,
  project_id  uuid references projects(id) on delete cascade,
  kind        text not null,
  actor       text not null,                -- 'agent'|'freelancer'|'outgoing'|'incoming'|'client'
  payload     jsonb,
  at          timestamptz default now()
);

create index events_project_at_idx on events(project_id, at desc);
create index items_project_state_idx on inventory_items(project_id, state, criticality desc);
```

**Invariants worth enforcing on Day 1:**
- The agent never mutates `events`. Only inserts.
- A project reaches `complete` only when *every* inventory item with criticality ≥ 2 is `verified` or `acknowledged`.
- A `decision` row without `resolved_at` blocks the agent from advancing.
- Every strategy switch writes an `attempts.next_action` — this is what makes the demo legible ("agent switched from *contact_outgoing* to *self_serve_from_log* because outgoing ignored the 3rd nudge").

---

## §05 · Bootstrap prompt

Paste this into Claude Code or Cursor on Day 1 as the seed context.

```
## Project: Overlap

You are helping scaffold Overlap: an autonomous handoff agent for freelance
project transitions. Submission target: Agents for Humans Hackathon on
Devpost (deadline Sep 14, 2026 · we ship Sep 6 for buffer).

The pitch: when a freelancer marks a project handing off, the agent inventories
what's in the outgoing dev's head, chases what only they can give, self-serves
what a log can reveal, briefs the incoming dev in their vocabulary, waits for
real acknowledgement, and only surfaces when a decision needs the human.

## Stack (non-negotiable)

- Frontend: Next.js 14 (app router) + TypeScript + TailwindCSS on Vercel
- Backend: Python 3.11 FastAPI + Strands Agents SDK
- Deployment: AWS Bedrock AgentCore (bonus points) with an App Runner fallback
- LLM: Anthropic Claude on Amazon Bedrock
- State: Supabase Postgres — the ONLY source of truth
- Tools: SES (email), poll-based reply checker, GitHub issues reader,
  CI-log secret extractor, Slack webhook sender, credential verifier

## Repo layout

overlap/
  apps/web/                Next.js dashboard + live status page
  services/agent/
    overlap/
      agent.py             top-level Strands agent + loop
      tools/               one file per tool
      state/               Postgres accessors
      prompts/             agent prompts, kept in .md files
  infra/schema.sql         the source-of-truth schema
  infra/bedrock.tf         AgentCore deployment (bonus)
  demo/seed.py             loads the fixture project into Postgres

## Behavior contract

- The agent is STATELESS between ticks. All memory lives in Postgres.
- On each tick, the agent:
    1. reads project + inventory + open threads
    2. picks the highest-priority unresolved item
    3. picks a strategy: contact_outgoing | self_serve_from_log |
       verify_credential | brief_incoming | escalate
    4. executes ONE action
    5. writes an events row and any state changes
- The agent only surfaces to the freelancer via the decisions table.
- Terminal state: every inventory_item with criticality >= 2 is in state
  'verified' or 'acknowledged'.

## What to build today (Day 1)

1. Scaffold the repo layout above with pnpm workspace + a Python package.
2. Write infra/schema.sql from the attached schema (see docs/overlap-plan.md §4).
3. Wire services/agent with a Strands "hello world" that reads a project row
   from Postgres and logs the inventory count. No agent logic beyond that.
4. Wire apps/web with a single /projects/[id] page that subscribes to the
   events table via Supabase Realtime and renders rows as they arrive.
5. Deploy web to Vercel, agent to a local Docker container for now.

## Do not build today

- Any real integration (Slack, GitHub, email — all mocked)
- Auth, billing, multi-project support
- Agent decision logic beyond "read and log"
- UI polish beyond default Tailwind

## The demo we're building toward

- Freelancer clicks "hand off Acme project"
- Agent inventories: 3 credentials, 4 open tickets, 3 undelivered
  promises, 2 head-only decisions
- Agent emails outgoing for POSTGRES_URL → outgoing ignores
- Agent switches strategy, extracts URL from CI log, verifies with \dt
- Agent asks outgoing ONLY the decision the log can't recover
  ("why Bun over Node?")
- Agent drafts incoming's onboarding, tailored to their Postgres version
- Incoming acks 4/7 → agent picks the 3 risky un-acked, sends
  a pointed follow-up on each
- The ONE moment the agent surfaces: "Close ticket #241? Client hasn't
  responded in 6 days" → freelancer clicks a chip
- HANDOFF COMPLETE

Ship each day's slice by end of day. On Day 6 the demo has to record clean.
```

---

## §06 · Demo shot list (90 seconds)

| Time | Beat | Voiceover |
|------|------|-----------|
| 0–5s | Title card: "Overlap — the handoff period, run by an agent." | Every project handoff needs an overlap. Almost none get one. |
| 5–15s | Dashboard: click "hand off Acme project" | A freelancer marks a project handing off. Then walks away. |
| 15–25s | Inventory column populates: 3 credentials, 4 tickets, 3 promises, 2 decisions | The agent inventories what's in the outgoing dev's head — twelve items across six kinds. |
| 25–40s | Split view: agent email to outgoing dev · outgoing's untouched inbox | It emails the outgoing dev for the database URL. Silence. |
| 40–55s | Strategy chip flips from `contact_outgoing` to `self_serve_from_log`; agent tool call to CI log; verify with `\dt`; item state → verified | So it changes strategy — pulls the URL from the CI log itself, verifies it, and moves on. |
| 55–70s | Incoming column populates with tailored briefings; ack tracker fills 4/7 | It drafts the incoming dev's briefing in their vocabulary. The dev acknowledges four of seven items. |
| 70–85s | Amber decision chip: "Close ticket #241? Client silent for 6 days" — freelancer clicks Resolve | The only moment it surfaces to the freelancer is a real decision the client hasn't answered. |
| 85–90s | Status flips to **Handoff complete**; event log scrolls | Handoff complete. Verified, not declared. |

---

## §07 · Cuts on sight

Behind by end of Day 4 or 5? Cut in this order.

1. **Real SES send.** Mock `email_send()` to write a row into `events`. The dashboard renders "email sent" from the event — no one can tell.
2. **Bedrock AgentCore.** Run the agent loop as a FastAPI background task with a Postgres-backed job cursor. Still durable in the way that matters.
3. **Real GitHub integration.** Inventory item source is a JSON fixture. Judges never see the source of the data.
4. **Real Slack.** Skip. If Day 6 buffer holds, a webhook post is the safest to re-add.
5. **Auth on the dashboard.** Hardcode a demo user in `middleware.ts`.
6. **Multiple projects.** Seed one. The rest is a scoped listing that's empty.
7. **Two-way incoming ack via real email.** Ack is a button on the briefing page linked from a mock notification.
8. **The blog post.** Costs 0.6 points and half a day — write it only if Day 7 morning is free.
