CREATE TABLE IF NOT EXISTS profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    company_name TEXT NOT NULL,
    company_description TEXT NOT NULL,
    topic_list TEXT[] NOT NULL,
    embedding VECTOR(1536) NOT NULL
);


create or replace function get_user_by_id(uid uuid)
returns table(email text) as $$
begin
  return query
  select email from auth.users where id = uid;
end;
$$ language plpgsql security definer;