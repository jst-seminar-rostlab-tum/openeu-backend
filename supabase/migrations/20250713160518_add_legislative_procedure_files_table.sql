drop function if exists "public"."match_filtered"(query_embedding vector, match_count integer, src_tables text[], content_columns text[]);

create table "public"."legislative_procedure_files" (
    "id" text not null,
    "link" text not null,
    "extracted_text" text not null,
    "scraped_at" timestamp with time zone not null default now()
);


CREATE UNIQUE INDEX legislative_procedure_files_pkey ON public.legislative_procedure_files USING btree (id);

alter table "public"."legislative_procedure_files" add constraint "legislative_procedure_files_pkey" PRIMARY KEY using index "legislative_procedure_files_pkey";

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.match_filtered(query_embedding vector, match_count integer, src_tables text[] DEFAULT NULL::text[], content_columns text[] DEFAULT NULL::text[], source_id_param text DEFAULT NULL::text)
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
      and (
        source_id_param is null
        or e.source_id = source_id_param)
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$function$
;

grant delete on table "public"."legislative_procedure_files" to "anon";

grant insert on table "public"."legislative_procedure_files" to "anon";

grant references on table "public"."legislative_procedure_files" to "anon";

grant select on table "public"."legislative_procedure_files" to "anon";

grant trigger on table "public"."legislative_procedure_files" to "anon";

grant truncate on table "public"."legislative_procedure_files" to "anon";

grant update on table "public"."legislative_procedure_files" to "anon";

grant delete on table "public"."legislative_procedure_files" to "authenticated";

grant insert on table "public"."legislative_procedure_files" to "authenticated";

grant references on table "public"."legislative_procedure_files" to "authenticated";

grant select on table "public"."legislative_procedure_files" to "authenticated";

grant trigger on table "public"."legislative_procedure_files" to "authenticated";

grant truncate on table "public"."legislative_procedure_files" to "authenticated";

grant update on table "public"."legislative_procedure_files" to "authenticated";

grant delete on table "public"."legislative_procedure_files" to "service_role";

grant insert on table "public"."legislative_procedure_files" to "service_role";

grant references on table "public"."legislative_procedure_files" to "service_role";

grant select on table "public"."legislative_procedure_files" to "service_role";

grant trigger on table "public"."legislative_procedure_files" to "service_role";

grant truncate on table "public"."legislative_procedure_files" to "service_role";

grant update on table "public"."legislative_procedure_files" to "service_role";


