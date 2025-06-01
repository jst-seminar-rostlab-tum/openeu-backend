CREATE TABLE IF NOT EXISTS spanish_commission_meetings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),  -- Unique identifier
  date DATE NOT NULL,                             -- Date of the event
  time TEXT,                                      -- Time of the event (optional)
  title TEXT NOT NULL,                            -- Title in original language
  title_en TEXT,                                  -- Translated title (optional)
  location TEXT,                                  -- Location in original language
  location_en TEXT,                               -- Translated location (optional)
  description TEXT,                               -- Description in original language
  description_en TEXT,                            -- Translated description (optional)
  url TEXT,                                       -- Main URL (optional)
  embedding_input TEXT,                           -- Text used to generate embedding
  links JSONB                                     -- Additional broadcast or info links as key-value pairs
);
