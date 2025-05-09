CREATE TABLE IF NOT EXISTS meeting_calendar (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    datetime TIMESTAMP NOT NULL,
    place TEXT,
    subtitles TEXT
);