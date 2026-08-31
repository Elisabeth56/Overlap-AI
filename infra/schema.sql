-- Overlap: source-of-truth schema for the handoff agent.
-- Six tables. Everything else is derived.
-- Invariants:
--   * events is append-only. Never update.
--   * projects.status = 'complete' only when every inventory_items row with
--     criticality >= 2 is 'verified' or 'acknowledged'.
--   * A decisions row with resolved_at IS NULL blocks the agent.
--   * Every strategy switch writes attempts.next_action.

create extension if not exists "pgcrypto";

-- Freelancer accounts (minimal for Day 1; auth deferred).
create table if not exists users (
  id          uuid primary key default gen_random_uuid(),
  handle      text unique not null,
  display     text,
  created_at  timestamptz default now()
);

create table if not exists projects (
  id                 uuid primary key default gen_random_uuid(),
  name               text not null,
  outgoing_owner_id  uuid not null references users(id),
  incoming_owner_id  uuid references users(id),
  client_ref         jsonb,
  status             text not null check (status in
    ('draft','inventorying','chasing_outgoing',
     'onboarding_incoming','verifying','complete','abandoned')),
  deadline           timestamptz,
  created_at         timestamptz default now()
);

create table if not exists inventory_items (
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

create table if not exists threads (
  id               uuid primary key default gen_random_uuid(),
  project_id       uuid references projects(id) on delete cascade,
  actor            text not null check (actor in ('outgoing','incoming','client')),
  channel          text not null check (channel in ('email','slack','sms')),
  subject          text,
  purpose          text not null,           -- "recover POSTGRES_URL"
  linked_item_id   uuid references inventory_items(id),
  status           text not null check (status in
    ('open','awaiting_reply','stalled','resolved','abandoned')),
  strategy         text,                    -- current strategy the agent is trying
  last_activity_at timestamptz
);

create table if not exists attempts (
  id             uuid primary key default gen_random_uuid(),
  thread_id      uuid references threads(id) on delete cascade,
  strategy       text not null,
  sent_at        timestamptz not null,
  message_body   text,
  reply_at       timestamptz,
  reply_summary  text,
  outcome        text check (outcome in
    ('answered','ignored','partial','refused','error')),
  next_action    text                        -- reason the strategy changes
);

create table if not exists decisions (      -- the "surfaces only for real decisions" gate
  id           uuid primary key default gen_random_uuid(),
  project_id   uuid references projects(id) on delete cascade,
  question     text not null,
  options      jsonb,
  raised_at    timestamptz default now(),
  resolved_at  timestamptz,
  resolved_by  uuid references users(id),
  resolution   jsonb
);

create table if not exists events (         -- append-only audit + status feed
  id          bigserial primary key,
  project_id  uuid references projects(id) on delete cascade,
  kind        text not null,
  actor       text not null,                -- 'agent'|'freelancer'|'outgoing'|'incoming'|'client'
  payload     jsonb,
  at          timestamptz default now()
);

create index if not exists events_project_at_idx  on events(project_id, at desc);
create index if not exists items_project_state_idx on inventory_items(project_id, state, criticality desc);

-- Enforce append-only on events.
create or replace function events_reject_mutation() returns trigger language plpgsql as $$
begin
  raise exception 'events is append-only';
end;
$$;

drop trigger if exists events_no_update on events;
create trigger events_no_update before update or delete on events
  for each row execute function events_reject_mutation();

-- Realtime for the dashboard event feed.
alter publication supabase_realtime add table events;
