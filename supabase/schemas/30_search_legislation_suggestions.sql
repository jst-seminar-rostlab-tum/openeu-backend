-- search_legislation_suggestions.sql
create extension if not exists pg_trgm;

create or replace function search_legislation_suggestions(search_text text)
returns table (
  id text,
  title text,
  similarity_score float
)
language sql
as $$
  select 
    id,
    title,
    similarity_score
  from (
    select 
      id,
      title,
      CASE 
        WHEN search_text <> '' AND (title ILIKE search_text || '%' OR id ILIKE search_text || '%') THEN 1.0
        ELSE GREATEST(
          similarity(title, search_text),
          similarity(id, search_text)
        )
    END AS similarity_score
    from legislative_files
    where (title is not null or id is not null)
  ) scored
  where similarity_score > 0.1
  order by similarity_score desc
  limit 5
$$; 
