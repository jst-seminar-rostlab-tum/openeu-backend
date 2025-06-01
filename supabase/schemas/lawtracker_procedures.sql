-- EU Law Procedures (aka “Law-Tracker by Topic”)
create table if not exists public.eu_law_procedures (
    id              text        primary key,
    title           text        not null,
    status          text,
    active_status   text,
    started_date    date,
    topic_codes     text[]      not null,
    topic_labels    text[]      not null,
    embedding_input text,
    updated_at      timestamptz default now()
);
