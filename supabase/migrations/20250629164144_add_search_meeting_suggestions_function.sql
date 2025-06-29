set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.get_meetings_by_filter(source_tables text[], source_ids text[], max_results integer, start_date timestamp with time zone DEFAULT NULL::timestamp with time zone, end_date timestamp with time zone DEFAULT NULL::timestamp with time zone, country text DEFAULT NULL::text, topics text[] DEFAULT NULL::text[])
 RETURNS SETOF v_meetings
 LANGUAGE sql
AS $function$
SELECT vm.*
FROM v_meetings vm
         JOIN unnest(source_tables, source_ids) AS src(source_table, source_id)
              ON vm.source_table = src.source_table
                  AND vm.source_id = src.source_id
WHERE (start_date IS NULL OR vm.meeting_start_datetime::date <= end_date::date)
  AND (end_date IS NULL OR COALESCE(vm.meeting_end_datetime, vm.meeting_start_datetime)::date >= start_date::date)
  AND (country IS NULL OR LOWER(vm.location) = LOWER(country))
  AND (topics IS NULL OR vm.topic = ANY(topics))
    LIMIT max_results;
$function$
;

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


