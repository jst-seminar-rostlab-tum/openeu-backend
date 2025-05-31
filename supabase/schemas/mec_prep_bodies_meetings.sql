CREATE TABLE IF NOT EXISTS mec_prep_bodies_meeting (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    meeting_timestamp TIMESTAMP NOT NULL,
    meeting_location TEXT NOT NULL,
    embedding_input TEXT NOT NULL,
    scraped_at timestamp with time zone NOT NULL DEFAULT now()
);
