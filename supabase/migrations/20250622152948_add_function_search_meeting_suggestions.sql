-- search_meetings_suggestions.sql

create or replace function search_meetings_suggestions(search_text text)
returns table (
  meeting_id text,
  title text,
  similarity_score float,
  meeting_start_datetime timestamptz,
  location text,
  topic text,
  source_id text,
  source_table text
)
language sql
as $$
  select 
    meeting_id,
    title,
    similarity(title, search_text) as similarity_score,
    meeting_start_datetime,
    location,
    topic,
    source_id,
    source_table
  from v_meetings
  where similarity(title, search_text) > 0.05
  order by similarity_score desc
  limit 5
$$;
