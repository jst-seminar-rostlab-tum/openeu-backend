set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.search_legislation_suggestions(search_text text)
 RETURNS TABLE(id text, title text, similarity_score double precision)
 LANGUAGE sql
AS $function$
  select DISTINCT
    id,
    title,
    similarity(title, search_text) as similarity_score
  from legislative_files
  where similarity(title, search_text) > 0.1
    and title is not null
  order by similarity_score desc
  limit 5
$function$
;


