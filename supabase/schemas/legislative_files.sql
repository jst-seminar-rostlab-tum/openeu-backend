create table if not exists public.legislative_files (
    id text primary key,
    link text,
    title text,
    lastpubdate text,
    details_link text,
    committee text,
    rapporteur text,
    status text,
    subjects jsonb,
    key_players jsonb,
    key_events jsonb,
    documentation_gateway jsonb,
    embedding_input text,
    scraped_at timestamp with time zone not null default now()
);
