CREATE TABLE IF NOT EXISTS meeting_topic_assignments (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    source_id TEXT NOT NULL,
    source_table TEXT NOT NULL,
    topic_id TEXT NOT NULL
    );