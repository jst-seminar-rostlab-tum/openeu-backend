CREATE TABLE IF NOT EXISTS legislative_files (
  reference   TEXT PRIMARY KEY,
  link        TEXT NOT NULL,
  title       TEXT NOT NULL,
  lastpubdate TEXT NOT NULL,
  committee   TEXT,
  rapporteur  TEXT
);