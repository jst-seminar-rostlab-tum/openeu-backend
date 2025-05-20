-- Austrian Parliament Meetings
CREATE TABLE IF NOT EXISTS austrian_parliament_meetings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title text NOT NULL,
    title_de text NOT NULL,
    meeting_type text NOT NULL,
    meeting_date date NOT NULL,
    meeting_location text NOT NULL,
    meeting_url text NOT NULL
);
