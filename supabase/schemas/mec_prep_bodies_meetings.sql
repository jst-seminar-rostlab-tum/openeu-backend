CREATE TABLE IF NOT EXISTS mec_prep_bodies_meeting (
    id INTEGER PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    meeting_timestamp TIMESTAMP NOT NULL,
    meeting_location TEXT NOT NULL,
    embedding_input TEXT NOT NULL
);