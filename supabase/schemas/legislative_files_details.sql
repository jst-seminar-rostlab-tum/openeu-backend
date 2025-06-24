create table if not exists public.legislative_files_details (
    id text primary key,
    link text,
    title text,
    status text,
    basic_info jsonb,
    subjects text[],
    key_players jsonb,
    key_events jsonb,
    scraped_at timestamp with time zone default now()
);
