-- EP Meetings
CREATE TABLE IF NOT EXISTS ep_meetings (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    title TEXT NOT NULL,
    datetime TIMESTAMP NOT NULL,
    place TEXT,
    subtitles TEXT,
    embedding_input TEXT,
    scraped_at timestamp with time zone NOT NULL DEFAULT now()
);