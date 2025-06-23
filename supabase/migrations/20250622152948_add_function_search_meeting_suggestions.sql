-- search_meetings_suggestions.sql
create extension if not exists pg_trgm;

create or replace function search_meetings_suggestions(search_text text)
returns table (
  title text,
  similarity_score float
)
language sql
as $$
  select DISTINCT
    title,
    similarity(title, search_text) as similarity_score
  from v_meetings
  where similarity(title, search_text) > 0.1
  order by similarity_score desc
  limit 5
$$;
