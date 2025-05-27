set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.match_default(query_embedding vector, match_count integer)
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
      ((1 - (e.embedding <#> query_embedding))/2)*100 as similarity
    from documents_embeddings e
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$function$
;

CREATE OR REPLACE FUNCTION public.match_filtered(src_tables text[], content_columns text[], query_embedding vector, match_count integer)
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
      ((1 - (e.embedding <#> query_embedding))/2)*100 as similarity
    from documents_embeddings e
    where
      e.source_table = any(src_tables)
      and e.content_column = any(content_columns)
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$function$
;


