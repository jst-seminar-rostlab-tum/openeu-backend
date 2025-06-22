create table if not exists public.legislative_files (
    reference text primary key,
    link text,
    title text,
    lastpubdate text,
    committee text,
    rapporteur text,
    embedding_input text,                
    scraped_at timestamp with time zone NOT NULL DEFAULT now()
);
