CREATE TABLE IF NOT EXISTS ec_res_inno_meetings (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    title TEXT NOT NULL,
    meeting_url TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    location TEXT NOT NULL,
    event_type TEXT NOT NULL,
    description TEXT NOT NULL,
    subjects TEXT[] DEFAULT '{}',
    embedding_input TEXT,
    scraped_at timestamp with time zone NOT NULL DEFAULT now()
);