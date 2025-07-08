-- Company table
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    company_stage TEXT NOT NULL,
    company_size INT NOT NULL,
    industry TEXT NOT NULL
);

-- Politician table
CREATE TABLE IF NOT EXISTS politicians (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    role TEXT NOT NULL,
    further_information TEXT,
    institution TEXT NOT NULL,
    area_of_expertise TEXT NOT NULL
);

CREATE TYPE user_type_enum AS ENUM ('entrepreneur', 'politician');

-- Profile table
CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    user_type user_type_enum NOT NULL DEFAULT 'entrepreneur', -- 'entrepreneur' or 'politician'
    company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
    politician_id UUID REFERENCES politicians(id) ON DELETE CASCADE,
    countries  TEXT[] NOT NULL DEFAULT '{}'::text[],
    newsletter_frequency TEXT NOT NULL DEFAULT 'none',
    embedding_input TEXT NOT NULL DEFAULT '',
    embedding VECTOR(1536) NOT NULL
);

CREATE TABLE IF NOT EXISTS profiles_to_topics (
    profile_id UUID NOT NULL,
    topic TEXT,
    topic_id TEXT NOT NULL,
    PRIMARY KEY (profile_id, topic_id),
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
