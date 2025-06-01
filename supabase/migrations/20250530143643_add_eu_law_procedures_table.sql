create table if not exists public.eu_law_procedures (
  procedure_id    text        primary key,
  title           text        not null,
  status          text,
  active_status   text,
  started_date    date,
  topic_codes     text[]      not null,
  topic_labels    text[]      not null,
  embedding_input text,
  updated_at      timestamptz default now()
);


grant select, insert, update, delete, truncate, references, trigger
  on table public.eu_law_procedures
  to anon;

grant select, insert, update, delete, truncate, references, trigger
  on table public.eu_law_procedures
  to authenticated;

grant select, insert, update, delete, truncate, references, trigger
  on table public.eu_law_procedures
  to service_role;