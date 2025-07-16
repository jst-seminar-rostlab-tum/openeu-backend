create table if not exists public.nl_twka_meetings (
  id                text         primary key,
  title             text,
  start_datetime    timestamptz,
  end_datetime      timestamptz,
  location          text,
  attachments_url   jsonb,
  original_title    text,
  translated_title  text,
  link              text,
  meeting_type      text,
  commission        text,
  start_time        time,
  end_time          time,
  agenda            jsonb,
  ministers         jsonb,
  attendees         jsonb,
  embedding_input   text,
  scraped_at        timestamptz  default now()
);


grant select, insert, update, delete, truncate, references, trigger
  on table public.nl_twka_meetings
  to anon;

grant select, insert, update, delete, truncate, references, trigger
  on table public.nl_twka_meetings
  to authenticated;

grant select, insert, update, delete, truncate, references, trigger
  on table public.nl_twka_meetings
  to service_role;