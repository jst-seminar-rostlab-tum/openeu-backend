CREATE TABLE IF NOT EXISTS polish_presidency_meeting (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    title TEXT NOT NULL,
    meeting_date DATE NOT NULL,
    meeting_end_date DATE,
    meeting_location TEXT NOT NULL,
    meeting_url TEXT NOT NULL,
    embedding_input TEXT,
    scraped_at timestamp with time zone NOT NULL DEFAULT now()
);