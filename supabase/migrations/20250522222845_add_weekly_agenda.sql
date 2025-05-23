-- +supabase_up
CREATE TABLE IF NOT EXISTS public.weekly_agenda (
  id          SERIAL PRIMARY KEY,
  type        TEXT NOT NULL,
  date        DATE NOT NULL,
  time        TEXT,
  title       TEXT NOT NULL,
  committee   TEXT,
  location    TEXT,
  description TEXT
);

-- +supabase_down
DROP TABLE IF EXISTS public.weekly_agenda;
