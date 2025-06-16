create table "public"."meeting_embeddings" (
    "id" text not null default (gen_random_uuid())::text,
    "source_table" text not null,
    "source_id" text not null,
    "content_column" text not null,
    "content_text" text not null,
    "embedding" vector(1536) not null,
    "created_at" timestamp with time zone default now()
);


alter table "public"."tweets" drop column "embedding_input";

CREATE INDEX meeting_embeddings_embedding_idx ON public.meeting_embeddings USING ivfflat (embedding) WITH (lists='100');

CREATE UNIQUE INDEX meeting_embeddings_pkey ON public.meeting_embeddings USING btree (id);

CREATE UNIQUE INDEX no_duplicates_meeting ON public.meeting_embeddings USING btree (source_table, source_id);

alter table "public"."meeting_embeddings" add constraint "meeting_embeddings_pkey" PRIMARY KEY using index "meeting_embeddings_pkey";

alter table "public"."meeting_embeddings" add constraint "no_duplicates_meeting" UNIQUE using index "no_duplicates_meeting";

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.match_combined_embeddings(query_embedding vector, match_count integer)
 RETURNS TABLE(source_table text, source_id text, content_text text, similarity double precision)
 LANGUAGE sql
 STABLE
AS $function$
  with all_embeddings as (
    select
      source_table,
      source_id,
      content_text,
      embedding
    from meeting_embeddings
    union all
    select
      source_table,
      source_id,
      content_text,
      embedding
    from documents_embeddings
  )
  select
    ae.source_table,
    ae.source_id,
    ae.content_text,
    -- convert cosine distance to a [0–1] similarity score
    ((1 - (ae.embedding <#> query_embedding))/2) as similarity
  from all_embeddings ae
  order by ae.embedding <#> query_embedding
  limit match_count;
$function$
;

CREATE OR REPLACE FUNCTION public.match_combined_filtered_embeddings(src_tables text[], query_embedding vector, match_count integer)
 RETURNS TABLE(source_table text, source_id text, content_text text, similarity double precision)
 LANGUAGE sql
 STABLE
AS $function$
  WITH all_embeddings AS (
    SELECT
      source_table,
      source_id,
      content_text,
      embedding
    FROM meeting_embeddings
    UNION ALL
    SELECT
      source_table,
      source_id,
      content_text,
      embedding
    FROM documents_embeddings
  )
  SELECT
    ae.source_table,
    ae.source_id,
    ae.content_text,
    ((1 - (ae.embedding <#> query_embedding))/2) AS similarity
  FROM all_embeddings ae
  WHERE ae.source_table = ANY(src_tables)
  ORDER BY ae.embedding <#> query_embedding
  LIMIT match_count;
$function$
;

CREATE OR REPLACE FUNCTION public.match_default_meetings(query_embedding vector, match_count integer)
 RETURNS TABLE(source_table text, source_id text, content_text text, similarity double precision)
 LANGUAGE plpgsql
AS $function$
declare
  max_dist float := sqrt(1536);
begin
  return query
    select
      e.source_table,
      e.source_id,
      e.content_text,
      ((1 - (e.embedding <#> query_embedding))/2) as similarity
    from meeting_embeddings e
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$function$
;

CREATE OR REPLACE FUNCTION public.match_filtered_meetings(src_tables text[], content_columns text[], query_embedding vector, match_count integer)
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
    from meeting_embeddings e
    where
      e.source_table = any(src_tables)
      and e.content_column = any(content_columns)
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$function$
;

grant delete on table "public"."meeting_embeddings" to "anon";

grant insert on table "public"."meeting_embeddings" to "anon";

grant references on table "public"."meeting_embeddings" to "anon";

grant select on table "public"."meeting_embeddings" to "anon";

grant trigger on table "public"."meeting_embeddings" to "anon";

grant truncate on table "public"."meeting_embeddings" to "anon";

grant update on table "public"."meeting_embeddings" to "anon";

grant delete on table "public"."meeting_embeddings" to "authenticated";

grant insert on table "public"."meeting_embeddings" to "authenticated";

grant references on table "public"."meeting_embeddings" to "authenticated";

grant select on table "public"."meeting_embeddings" to "authenticated";

grant trigger on table "public"."meeting_embeddings" to "authenticated";

grant truncate on table "public"."meeting_embeddings" to "authenticated";

grant update on table "public"."meeting_embeddings" to "authenticated";

grant delete on table "public"."meeting_embeddings" to "service_role";

grant insert on table "public"."meeting_embeddings" to "service_role";

grant references on table "public"."meeting_embeddings" to "service_role";

grant select on table "public"."meeting_embeddings" to "service_role";

grant trigger on table "public"."meeting_embeddings" to "service_role";

grant truncate on table "public"."meeting_embeddings" to "service_role";

grant update on table "public"."meeting_embeddings" to "service_role";


