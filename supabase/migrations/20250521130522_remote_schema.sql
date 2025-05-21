create extension if not exists "vector" with schema "public" version '0.8.0';

revoke delete on table "public"."meps" from "anon";

revoke insert on table "public"."meps" from "anon";

revoke references on table "public"."meps" from "anon";

revoke select on table "public"."meps" from "anon";

revoke trigger on table "public"."meps" from "anon";

revoke truncate on table "public"."meps" from "anon";

revoke update on table "public"."meps" from "anon";

revoke delete on table "public"."meps" from "authenticated";

revoke insert on table "public"."meps" from "authenticated";

revoke references on table "public"."meps" from "authenticated";

revoke select on table "public"."meps" from "authenticated";

revoke trigger on table "public"."meps" from "authenticated";

revoke truncate on table "public"."meps" from "authenticated";

revoke update on table "public"."meps" from "authenticated";

revoke delete on table "public"."meps" from "service_role";

revoke insert on table "public"."meps" from "service_role";

revoke references on table "public"."meps" from "service_role";

revoke select on table "public"."meps" from "service_role";

revoke trigger on table "public"."meps" from "service_role";

revoke truncate on table "public"."meps" from "service_role";

revoke update on table "public"."meps" from "service_role";

revoke delete on table "public"."scheduled_job_runs" from "anon";

revoke insert on table "public"."scheduled_job_runs" from "anon";

revoke references on table "public"."scheduled_job_runs" from "anon";

revoke select on table "public"."scheduled_job_runs" from "anon";

revoke trigger on table "public"."scheduled_job_runs" from "anon";

revoke truncate on table "public"."scheduled_job_runs" from "anon";

revoke update on table "public"."scheduled_job_runs" from "anon";

revoke delete on table "public"."scheduled_job_runs" from "authenticated";

revoke insert on table "public"."scheduled_job_runs" from "authenticated";

revoke references on table "public"."scheduled_job_runs" from "authenticated";

revoke select on table "public"."scheduled_job_runs" from "authenticated";

revoke trigger on table "public"."scheduled_job_runs" from "authenticated";

revoke truncate on table "public"."scheduled_job_runs" from "authenticated";

revoke update on table "public"."scheduled_job_runs" from "authenticated";

revoke delete on table "public"."scheduled_job_runs" from "service_role";

revoke insert on table "public"."scheduled_job_runs" from "service_role";

revoke references on table "public"."scheduled_job_runs" from "service_role";

revoke select on table "public"."scheduled_job_runs" from "service_role";

revoke trigger on table "public"."scheduled_job_runs" from "service_role";

revoke truncate on table "public"."scheduled_job_runs" from "service_role";

revoke update on table "public"."scheduled_job_runs" from "service_role";

alter table "public"."meps" drop constraint "meps_pkey";

alter table "public"."scheduled_job_runs" drop constraint "scheduled_job_runs_pkey";

drop index if exists "public"."meps_pkey";

drop index if exists "public"."scheduled_job_runs_pkey";

drop table "public"."meps";

drop table "public"."scheduled_job_runs";

create table "public"."documents_embeddings" (
    "id" uuid not null default gen_random_uuid(),
    "source_table" text not null,
    "source_id" text not null,
    "content_column" text not null,
    "content_text" text not null,
    "embedding" vector(1536) not null,
    "created_at" timestamp with time zone default now()
);


CREATE INDEX documents_embeddings_embedding_idx ON public.documents_embeddings USING ivfflat (embedding) WITH (lists='100');

CREATE UNIQUE INDEX documents_embeddings_pkey ON public.documents_embeddings USING btree (id);

CREATE UNIQUE INDEX no_duplicates ON public.documents_embeddings USING btree (source_table, source_id, content_text);

alter table "public"."documents_embeddings" add constraint "documents_embeddings_pkey" PRIMARY KEY using index "documents_embeddings_pkey";

alter table "public"."documents_embeddings" add constraint "no_duplicates" UNIQUE using index "no_duplicates";

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.match_filtered(src_tables text[], content_columns text[], query_embedding vector, match_count integer)
 RETURNS TABLE(source_table text, source_id text, content_text text, similarity double precision)
 LANGUAGE plpgsql
AS $function$
begin
  return query
    select
      e.source_table,
      e.source_id,
      e.content_text,
      1 - (e.embedding <#> query_embedding) as similarity
    from documents_embeddings e
    where
      e.source_table = any(src_tables)
      and e.content_column = any(content_columns)
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$function$
;

grant delete on table "public"."documents_embeddings" to "anon";

grant insert on table "public"."documents_embeddings" to "anon";

grant references on table "public"."documents_embeddings" to "anon";

grant select on table "public"."documents_embeddings" to "anon";

grant trigger on table "public"."documents_embeddings" to "anon";

grant truncate on table "public"."documents_embeddings" to "anon";

grant update on table "public"."documents_embeddings" to "anon";

grant delete on table "public"."documents_embeddings" to "authenticated";

grant insert on table "public"."documents_embeddings" to "authenticated";

grant references on table "public"."documents_embeddings" to "authenticated";

grant select on table "public"."documents_embeddings" to "authenticated";

grant trigger on table "public"."documents_embeddings" to "authenticated";

grant truncate on table "public"."documents_embeddings" to "authenticated";

grant update on table "public"."documents_embeddings" to "authenticated";

grant delete on table "public"."documents_embeddings" to "service_role";

grant insert on table "public"."documents_embeddings" to "service_role";

grant references on table "public"."documents_embeddings" to "service_role";

grant select on table "public"."documents_embeddings" to "service_role";

grant trigger on table "public"."documents_embeddings" to "service_role";

grant truncate on table "public"."documents_embeddings" to "service_role";

grant update on table "public"."documents_embeddings" to "service_role";


