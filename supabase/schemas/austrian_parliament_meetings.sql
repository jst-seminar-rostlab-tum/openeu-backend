-- Austrian Parliament Meetings
CREATE TABLE IF NOT EXISTS austrian_parliament_meetings (
    id text PRIMARY KEY,
    title text NOT NULL,
    title_de text NOT NULL,
    meeting_type text NOT NULL,
    meeting_date date NOT NULL,
    meeting_location text NOT NULL,
    meeting_url text NOT NULL,
    embedding_input text NOT NULL,
    scraped_at timestamp with time zone NOT NULL DEFAULT now()
);
