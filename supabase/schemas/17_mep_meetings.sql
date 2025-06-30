-- MEP Meetings
CREATE TABLE IF NOT EXISTS mep_meetings (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    title text NOT NULL,
    member_name text NOT NULL,
    meeting_date date NOT NULL,
    meeting_location text NOT NULL,
    member_capacity text NOT NULL,
    procedure_reference text,
    associated_committee_or_delegation_code text,
    associated_committee_or_delegation_name text,
    embedding_input TEXT,
    scraped_at timestamp with time zone NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS mep_meeting_attendees (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    name text NOT NULL,
    transparency_register_url text UNIQUE
);

CREATE TABLE IF NOT EXISTS mep_meeting_attendee_mapping (
    meeting_id TEXT REFERENCES mep_meetings(id) ON DELETE CASCADE,
    attendee_id TEXT REFERENCES mep_meeting_attendees(id) ON DELETE CASCADE,
    PRIMARY KEY (meeting_id, attendee_id)
);