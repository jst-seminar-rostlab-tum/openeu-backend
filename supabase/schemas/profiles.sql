CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    company_name TEXT NOT NULL,
    company_description TEXT NOT NULL,
    topic_list TEXT[] NOT NULL,
    countries  TEXT[] NOT NULL DEFAULT '{}'::text[],
    newsletter_frequency TEXT NOT NULL DEFAULT 'none',
    embedding VECTOR(1536) NOT NULL
);

CREATE TABLE IF NOT EXISTS profiles_to_topics (
    profile_id UUID,
    topic TEXT,
    topic_id TEXT,
    FOREIGN KEY (profile_id) REFERENCES public.profiles(id) ON DELETE CASCADE,
    FOREIGN KEY (topic_id) REFERENCES public.meeting_topics(id) ON DELETE CASCADE
);

CREATE OR REPLACE FUNCTION get_user_by_id(uid UUID)
  RETURNS TEXT
AS $$
  SELECT email
    FROM auth.users
   WHERE id = $1;
$$
LANGUAGE SQL
SECURITY DEFINER;
