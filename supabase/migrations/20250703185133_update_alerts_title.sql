alter table "public"."alerts" add column "title" text not null;

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.search_legislation_suggestions(search_text text)
 RETURNS TABLE(id text, title text, similarity_score double precision)
 LANGUAGE sql
AS $function$
  select 
    id,
    title,
    similarity_score
  from (
    select 
      id,
      title,
      GREATEST(
        similarity(title, search_text),
        similarity(id, search_text)
      ) as similarity_score
    from legislative_files
    where (title is not null or id is not null)
  ) scored
  where similarity_score > 0.1
  order by similarity_score desc
  limit 5
$function$
;


