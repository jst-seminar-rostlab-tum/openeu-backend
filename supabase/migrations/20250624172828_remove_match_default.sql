drop function if exists "public"."match_default"(query_embedding vector, match_count integer);

drop function if exists "public"."match_filtered"(src_tables text[], content_columns text[], query_embedding vector, match_count integer);

set check_function_bodies = off;

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
      (
        src_tables is null
        or e.source_table = any(src_tables))
      and (
        content_columns is null
        or e.content_column = any(content_columns))
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$function$
;


