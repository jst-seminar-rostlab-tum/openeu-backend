CREATE TABLE IF NOT EXISTS spanish_commission_meetings (
  id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,         -- Unique identifier as text
  date DATE NOT NULL,                                          -- Date of the event
  time TEXT,                                                   -- Time of the event (optional)
  title TEXT NOT NULL,                                         -- Title in original language
  title_english TEXT,                                               -- Translated title (optional)
  location TEXT,                                               -- Location in original language
  location_english TEXT,                                            -- Translated location (optional)
  description TEXT,                                            -- Description in original language
  description_english TEXT,                                         -- Translated description (optional)
  url TEXT,                                                    -- Main URL (optional)
  embedding_input TEXT,                                        -- Text used to generate embedding
  links JSONB,                                                 -- Additional broadcast or info links as key-value pairs
  scraped_at timestamp with time zone NOT NULL DEFAULT now()   -- Timestamp of when the entry was scraped
);
