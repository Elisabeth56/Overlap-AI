-- Day 1 fixture: one user, one project. Enough for the hello-world.
-- Idempotent: safe to re-run.
insert into users (id, handle, display)
values ('00000000-0000-0000-0000-000000000001', 'elisabeth', 'Elisabeth')
on conflict (handle) do nothing;

insert into projects (id, name, outgoing_owner_id, status)
values (
  '11111111-1111-1111-1111-111111111111',
  'Acme Redesign',
  '00000000-0000-0000-0000-000000000001',
  'draft'
)
on conflict (id) do nothing;
