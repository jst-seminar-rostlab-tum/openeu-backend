drop function if exists "public"."match_filtered_meetings"(query_embedding vector, match_count integer, src_tables text[], content_columns text[], allowed_topics text[], allowed_topic_ids text[], allowed_countries text[]);

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.match_filtered_meetings(query_embedding vector, match_count integer, src_tables text[] DEFAULT NULL::text[], content_columns text[] DEFAULT NULL::text[], allowed_topics text[] DEFAULT NULL::text[], allowed_topic_ids text[] DEFAULT NULL::text[], allowed_countries text[] DEFAULT NULL::text[], start_date timestamptz DEFAULT NULL::timestamptz, end_date timestamptz DEFAULT NULL::timestamptz)
 RETURNS TABLE(source_table text, source_id text, content_text text, similarity double precision)
 LANGUAGE plpgsql
AS $function$
begin
  return query
    select
      e.source_table,
      e.source_id,
      e.content_text,
      ((1 - (e.embedding <#> query_embedding)) / 2) as similarity
    from meeting_embeddings e
    
    where
      -- optional table filter
      (src_tables is null
       or e.source_table = any(src_tables)
      )
      -- optional column filter
      and (content_columns is null
           or e.content_column = any(content_columns)
          )
          
      -- optional topic filter using EXISTS
      and (
        allowed_topic_ids is null
        or exists (
          select 1 from meeting_topic_assignments mta
           where mta.source_table = e.source_table
             and mta.source_id    = e.source_id
             and mta.topic_id = any(allowed_topic_ids)
        )
      )

      and (
        allowed_topics is null
        or exists (
          select 1 from meeting_topic_assignments mta, meeting_topics mt
           where mta.source_table = e.source_table
             and mta.source_id    = e.source_id
             and mta.topic_id = mt.id
             and mt.topic = any(allowed_topics)
        )
      )

      -- optional country filter using EXISTS (only for profiles)
      
    AND (
      allowed_countries IS NULL
      OR LOWER((
        SELECT vm.location
        FROM public.v_meetings vm
        WHERE vm.source_table = e.source_table
          AND vm.source_id = e.source_id)) = ANY (
        SELECT LOWER(country) FROM unnest(allowed_countries) AS country
      )
    )

    AND (end_date IS NULL OR (
        SELECT vm.meeting_start_datetime::date
        FROM public.v_meetings vm
         WHERE vm.source_table = e.source_table
           AND vm.source_id   = e.source_id
        LIMIT 1
    ) <= end_date::date)

    AND (start_date IS NULL OR (
        SELECT COALESCE(vm.meeting_end_datetime, vm.meeting_start_datetime)::date
        FROM public.v_meetings vm
         WHERE vm.source_table = e.source_table
           AND vm.source_id   = e.source_id
        LIMIT 1
    ) >= start_date::date)
    
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$function$
;


