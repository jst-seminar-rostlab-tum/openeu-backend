CREATE TABLE IF NOT EXISTS mec_summit_ministerial_meeting (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    meeting_date DATE NOT NULL,
    meeting_end_date DATE,
    category_abbr TEXT
);
