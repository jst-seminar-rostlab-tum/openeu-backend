-- EP Meetings
CREATE TABLE IF NOT EXISTS ep_meetings (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    datetime TIMESTAMP NOT NULL,
    place TEXT,
    subtitles TEXT
);