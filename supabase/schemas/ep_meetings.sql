-- EP Meetings
CREATE TABLE IF NOT EXISTS ep_meetings (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    datetime TIMESTAMP NOT NULL,
    place TEXT,
    subtitles TEXT
);

-- MEP Meetings
CREATE TABLE IF NOT EXISTS mep_meetings (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    title text NOT NULL,
    member_name text NOT NULL,
    meeting_date date NOT NULL,
    meeting_location text NOT NULL,
    member_capacity text NOT NULL,
    procedure_reference text,
    associated_committee_or_delegation_code text,
    associated_committee_or_delegation_name text
);

CREATE TABLE IF NOT EXISTS mep_meeting_attendees (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name text NOT NULL,
    transparency_register_url text UNIQUE
);

CREATE TABLE IF NOT EXISTS mep_meeting_attendee_mapping (
    meeting_id uuid REFERENCES mep_meetings(id) ON DELETE CASCADE,
    attendee_id uuid REFERENCES mep_meeting_attendees(id) ON DELETE CASCADE,
    PRIMARY KEY (meeting_id, attendee_id)
);