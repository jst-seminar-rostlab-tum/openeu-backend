-- saves all alerts requested by users (last_run_at != NULL  => alert was processed)
--when an email is sent out by a smart_alert, it is logged in the existing public.notifications table
create table alerts (
  id                   uuid primary key default gen_random_uuid(),
  user_id              uuid references auth.users not null,
  description          text not null,
  embedding            vector(1536),
  title                text not null,
  relevancy_threshold  real not null default 0.95,
  last_run_at          timestamptz,
  is_active            boolean not null default true,
  created_at           timestamptz default now(),
  updated_at           timestamptz default now()
);
