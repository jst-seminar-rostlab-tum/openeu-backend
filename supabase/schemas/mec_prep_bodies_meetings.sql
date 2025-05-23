CREATE TABLE IF NOT EXISTS mec_prep_bodies_meeting (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    meeting_date DATE NOT NULL,
    prep_body_abbr TEXT NOT NULL,
);

-- TODO: add location, time, etc
