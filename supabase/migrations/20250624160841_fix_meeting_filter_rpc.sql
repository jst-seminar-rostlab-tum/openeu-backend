drop function if exists "public"."match_combined_embeddings"(query_embedding vector, match_count integer);

drop function if exists "public"."match_combined_filtered_embeddings"(src_tables text[], query_embedding vector, match_count integer);

drop function if exists "public"."match_default_meetings"(query_embedding vector, match_count integer);

drop function if exists "public"."match_filtered_meetings"(src_tables text[], content_columns text[], query_embedding vector, match_count integer);

create table "public"."profiles_to_topics" (
    "profile_id" uuid,
    "topic" text,
    "topic_id" text
);


alter table "public"."profiles" add column "countries" text[] not null default '{}'::text[];

alter table "public"."profiles_to_topics" add constraint "profiles_to_topics_profile_id_fkey" FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE not valid;

alter table "public"."profiles_to_topics" validate constraint "profiles_to_topics_profile_id_fkey";

alter table "public"."profiles_to_topics" add constraint "profiles_to_topics_topic_id_fkey" FOREIGN KEY (topic_id) REFERENCES meeting_topics(id) ON DELETE CASCADE not valid;

alter table "public"."profiles_to_topics" validate constraint "profiles_to_topics_topic_id_fkey";

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

CREATE OR REPLACE FUNCTION public.match_filtered_meetings(query_embedding vector, match_count integer, src_tables text[] DEFAULT NULL::text[], content_columns text[] DEFAULT NULL::text[], allowed_topics text[] DEFAULT NULL::text[], allowed_topic_ids text[] DEFAULT NULL::text[], allowed_countries text[] DEFAULT NULL::text[])
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
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$function$
;

grant delete on table "public"."profiles_to_topics" to "anon";

grant insert on table "public"."profiles_to_topics" to "anon";

grant references on table "public"."profiles_to_topics" to "anon";

grant select on table "public"."profiles_to_topics" to "anon";

grant trigger on table "public"."profiles_to_topics" to "anon";

grant truncate on table "public"."profiles_to_topics" to "anon";

grant update on table "public"."profiles_to_topics" to "anon";

grant delete on table "public"."profiles_to_topics" to "authenticated";

grant insert on table "public"."profiles_to_topics" to "authenticated";

grant references on table "public"."profiles_to_topics" to "authenticated";

grant select on table "public"."profiles_to_topics" to "authenticated";

grant trigger on table "public"."profiles_to_topics" to "authenticated";

grant truncate on table "public"."profiles_to_topics" to "authenticated";

grant update on table "public"."profiles_to_topics" to "authenticated";

grant delete on table "public"."profiles_to_topics" to "service_role";

grant insert on table "public"."profiles_to_topics" to "service_role";

grant references on table "public"."profiles_to_topics" to "service_role";

grant select on table "public"."profiles_to_topics" to "service_role";

grant trigger on table "public"."profiles_to_topics" to "service_role";

grant truncate on table "public"."profiles_to_topics" to "service_role";

grant update on table "public"."profiles_to_topics" to "service_role";


