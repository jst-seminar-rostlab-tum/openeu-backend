drop function if exists "public"."match_combined_embeddings"(query_embedding vector, match_count integer);

drop function if exists "public"."match_combined_filtered_embeddings"(src_tables text[], content_columns text[], query_embedding vector, match_count integer);

drop function if exists "public"."match_combined_filtered_embeddings"(src_tables text[], query_embedding vector, match_count integer);

drop function if exists "public"."match_default_meetings"(query_embedding vector, match_count integer);

drop function if exists "public"."match_filtered"(src_tables text[], content_columns text[], query_embedding vector, match_count integer);

drop function if exists "public"."match_filtered_meetings"(src_tables text[], content_columns text[], query_embedding vector, match_count integer, allowed_topic_ids text[], allowed_countries text[]);

drop function if exists "public"."match_default"(query_embedding vector, match_count integer);

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.match_combined_filtered_embeddings(query_embedding vector, match_count integer, src_tables text[] DEFAULT NULL::text[], content_columns text[] DEFAULT NULL::text[])
 RETURNS TABLE(source_table text, source_id text, content_text text, similarity double precision)
 LANGUAGE sql
 STABLE
AS $function$
  WITH all_embeddings AS (
    SELECT
      source_table,
      source_id,
      content_text,
      content_column,
      embedding
    FROM meeting_embeddings
    UNION ALL
    SELECT
      source_table,
      source_id,
      content_text,
      content_column,
      embedding
    FROM documents_embeddings
  )
  SELECT
    ae.source_table,
    ae.source_id,
    ae.content_text,
    ((1 - (ae.embedding <#> query_embedding))/2) AS similarity
  FROM all_embeddings ae
  WHERE (src_tables IS NULL or ae.source_table = ANY(src_tables)) and (content_columns IS NULL or ae.content_column = ANY(content_columns))
  ORDER BY ae.embedding <#> query_embedding
  LIMIT match_count;
$function$
;

CREATE OR REPLACE FUNCTION public.match_filtered(query_embedding vector, match_count integer, src_tables text[] DEFAULT NULL::text[], content_columns text[] DEFAULT NULL::text[])
 RETURNS TABLE(source_table text, source_id text, content_text text, similarity double precision)
 LANGUAGE plpgsql
AS $function$
declare
  max_dist float := sqrt(1536);  -- approx. 39.1918
begin
  return query
    select
      e.source_table,
      e.source_id,
      e.content_text,
      ((1 - (e.embedding <#> query_embedding))/2) as similarity
    from documents_embeddings e
    where
      (src_tables = NULL or e.source_table = any(src_tables)) and
      (content_columns = NULL or e.content_column = any(content_columns))
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$function$
;


