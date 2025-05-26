-- Belgian Parliament Meetings
CREATE TABLE IF NOT EXISTS belgian_parliament_meetings (
    id integer PRIMARY KEY,
    title text NOT NULL,
    title_en text NOT NULL,
    description text,
    description_en text,
    meeting_date date NOT NULL,
    location text NOT NULL,
    meeting_url text NOT NULL,
    embedding_input text NOT NULL
);
