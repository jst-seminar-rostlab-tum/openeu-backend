-- 1. Create the alerts frequency enum
create type alert_frequency as enum ('daily', 'weekly', 'monthly');

-- 2. Create alerts table
create table alerts (
  id                   uuid primary key default gen_random_uuid(),
  user_id              uuid references auth.users not null,
  description          text not null,
  embedding            vector(1536),
  frequency            alert_frequency not null default 'daily',
  relevancy_threshold  real not null default 0.75,
  last_run_at          timestamptz,
  is_active            boolean not null default true,
  created_at           timestamptz default now(),
  updated_at           timestamptz default now()
);

-- 3. Create alert_notifications table
create table alert_notifications (
  id           uuid primary key default gen_random_uuid(),
  alert_id     uuid references alerts on delete cascade,
  meeting_id   text not null,    -- now just a free-form ID matching v_meetings.meeting_id
  similarity   real,
  sent_at      timestamptz default now()
);

-- 4. Grant permissions on alerts
grant select, insert, update, delete, truncate, references, trigger
  on table public.alerts
  to anon;

grant select, insert, update, delete, truncate, references, trigger
  on table public.alerts
  to authenticated;

grant select, insert, update, delete, truncate, references, trigger
  on table public.alerts
  to service_role;

-- 5. Grant permissions on alert_notifications
grant select, insert, update, delete, truncate, references, trigger
  on table public.alert_notifications
  to anon;

grant select, insert, update, delete, truncate, references, trigger
  on table public.alert_notifications
  to authenticated;

grant select, insert, update, delete, truncate, references, trigger
  on table public.alert_notifications
  to service_role;
