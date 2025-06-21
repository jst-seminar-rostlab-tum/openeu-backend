create table "public"."profiles_to_countries" (
    "profile_id" uuid,
    "country" text
);


create table "public"."profiles_to_topics" (
    "profile_id" uuid,
    "topic_id" text
);


alter table "public"."profiles_to_countries" add constraint "profiles_to_countries_profile_id_fkey" FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE not valid;

alter table "public"."profiles_to_countries" validate constraint "profiles_to_countries_profile_id_fkey";

alter table "public"."profiles_to_topics" add constraint "profiles_to_topics_profile_id_fkey" FOREIGN KEY (profile_id) REFERENCES profiles(id) ON DELETE CASCADE not valid;

alter table "public"."profiles_to_topics" validate constraint "profiles_to_topics_profile_id_fkey";

alter table "public"."profiles_to_topics" add constraint "profiles_to_topics_topic_id_fkey" FOREIGN KEY (topic_id) REFERENCES meeting_topics(id) ON DELETE CASCADE not valid;

alter table "public"."profiles_to_topics" validate constraint "profiles_to_topics_topic_id_fkey";

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.match_filtered_meetings(src_tables text[], content_columns text[], query_embedding vector, match_count integer, allowed_topic_ids text[] DEFAULT NULL::text[], allowed_countries text[] DEFAULT NULL::text[])
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

    -- join topics
    left join meeting_topic_assignments mta
      on e.source_table = mta.source_table
     and e.source_id    = mta.source_id

    -- join countries (profiles only)
    left join profiles_to_countries ptc
      on e.source_table = 'profiles'
     and e.source_id    = ptc.profile_id

    where
      e.source_table    = any(src_tables)
      and e.content_column = any(content_columns)

      -- topic filter
      and (
        allowed_topic_ids is null
        or mta.topic_id = any(allowed_topic_ids)
      )

      -- country filter
      and (
        allowed_countries is null
        or (
          e.source_table = 'profiles'
          and ptc.country = any(allowed_countries)
        )
      )

    order by e.embedding <#> query_embedding
    limit match_count;
end;
$function$
;

grant delete on table "public"."profiles_to_countries" to "anon";

grant insert on table "public"."profiles_to_countries" to "anon";

grant references on table "public"."profiles_to_countries" to "anon";

grant select on table "public"."profiles_to_countries" to "anon";

grant trigger on table "public"."profiles_to_countries" to "anon";

grant truncate on table "public"."profiles_to_countries" to "anon";

grant update on table "public"."profiles_to_countries" to "anon";

grant delete on table "public"."profiles_to_countries" to "authenticated";

grant insert on table "public"."profiles_to_countries" to "authenticated";

grant references on table "public"."profiles_to_countries" to "authenticated";

grant select on table "public"."profiles_to_countries" to "authenticated";

grant trigger on table "public"."profiles_to_countries" to "authenticated";

grant truncate on table "public"."profiles_to_countries" to "authenticated";

grant update on table "public"."profiles_to_countries" to "authenticated";

grant delete on table "public"."profiles_to_countries" to "service_role";

grant insert on table "public"."profiles_to_countries" to "service_role";

grant references on table "public"."profiles_to_countries" to "service_role";

grant select on table "public"."profiles_to_countries" to "service_role";

grant trigger on table "public"."profiles_to_countries" to "service_role";

grant truncate on table "public"."profiles_to_countries" to "service_role";

grant update on table "public"."profiles_to_countries" to "service_role";

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


