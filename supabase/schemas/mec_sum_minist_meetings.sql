CREATE TABLE mec_summit_ministerial_meeting (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL UNIQUE,
    title TEXT NOT NULL,
    meeting_date DATE NOT NULL,
    meeting_end_date DATE,
    category_abbr TEXT
);
