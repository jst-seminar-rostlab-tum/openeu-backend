-- 1. Create alerts table
create table alerts (
  id                   uuid primary key default gen_random_uuid(),
  user_id              uuid references auth.users not null,
  description          text not null,
  embedding            vector(1536),
  relevancy_threshold  real not null default 0.95,
  last_run_at          timestamptz,
  is_active            boolean not null default true,
  created_at           timestamptz default now(),
  updated_at           timestamptz default now()
);


-- 2. Grant permissions on alerts
grant select, insert, update, delete, truncate, references, trigger
  on table public.alerts
  to anon;

grant select, insert, update, delete, truncate, references, trigger
  on table public.alerts
  to authenticated;

grant select, insert, update, delete, truncate, references, trigger
  on table public.alerts
  to service_role;