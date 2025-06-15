CREATE TABLE IF NOT EXISTS meeting_topics (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    topic TEXT NOT NULL
    );