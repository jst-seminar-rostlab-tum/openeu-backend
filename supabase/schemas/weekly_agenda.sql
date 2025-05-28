CREATE TABLE IF NOT EXISTS weekly_agenda (
  id          TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,       -- Unique identifier for each entry
  type        TEXT NOT NULL,            -- Type of event (e.g., "Plenary session", "Delegation")
  date        DATE NOT NULL,            -- Date of the event
  time        TEXT,                     -- Time of the event (optional)
  title       TEXT NOT NULL,            -- Title of the event
  committee   TEXT,                     -- Committee involved (optional)
  location    TEXT,                     -- Location of the event (optional)
  description TEXT,                     -- Additional details or topics (optional)
  embedding_input  TEXT                 -- concatenated field for embeddings
);