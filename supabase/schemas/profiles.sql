CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    company_name TEXT NOT NULL,
    company_description TEXT NOT NULL,
    topic_list TEXT[] NOT NULL,
    newsletter_frequency TEXT NOT NULL DEFAULT 'none',
    embedding VECTOR(1536) NOT NULL
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
