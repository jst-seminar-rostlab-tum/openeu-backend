-- search_legislation_suggestions.sql
create extension if not exists pg_trgm;

create or replace function search_legislation_suggestions(search_text text)
returns table (
  reference text,
  title text,
  similarity_score float
)
language sql
as $$
  select DISTINCT
    reference,
    title,
    similarity(title, search_text) as similarity_score
  from legislative_files
  where similarity(title, search_text) > 0.1
    and title is not null
  order by similarity_score desc
  limit 5
$$; 