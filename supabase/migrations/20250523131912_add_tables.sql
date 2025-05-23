create extension if not exists "vector" with schema "public" version '0.8.0';

create sequence "public"."ep_meetings_id_seq";

create table "public"."austrian_parliament_meetings" (
    "id" uuid not null default gen_random_uuid(),
    "title" text not null,
    "title_de" text not null,
    "meeting_type" text not null,
    "meeting_date" date not null,
    "meeting_location" text not null,
    "meeting_url" text not null
);


create table "public"."bt_documents" (
    "id" text not null,
    "datum" date,
    "titel" text,
    "drucksachetyp" text,
    "text" text
);


create table "public"."bt_plenarprotokolle" (
    "id" text not null,
    "datum" date,
    "titel" text,
    "sitzungsbemerkung" text,
    "text" text
);


create table "public"."documents_embeddings" (
    "id" uuid not null default gen_random_uuid(),
    "source_table" text not null,
    "source_id" text not null,
    "content_column" text not null,
    "content_text" text not null,
    "embedding" vector(1536) not null,
    "created_at" timestamp with time zone default now()
);


create table "public"."ep_meetings" (
    "id" integer not null default nextval('ep_meetings_id_seq'::regclass),
    "title" text not null,
    "datetime" timestamp without time zone not null,
    "place" text,
    "subtitles" text
);


create table "public"."ipex_events" (
    "id" text not null,
    "title" text not null,
    "start_date" date,
    "end_date" date,
    "meeting_location" text,
    "tags" text[]
);


create table "public"."legislative_files" (
    "reference" text not null,
    "link" text not null,
    "title" text not null,
    "lastpubdate" text not null,
    "committee" text,
    "rapporteur" text
);


create table "public"."mep_meeting_attendee_mapping" (
    "meeting_id" uuid not null,
    "attendee_id" uuid not null
);


create table "public"."mep_meeting_attendees" (
    "id" uuid not null default gen_random_uuid(),
    "name" text not null,
    "transparency_register_url" text
);


create table "public"."mep_meetings" (
    "id" uuid not null default gen_random_uuid(),
    "title" text not null,
    "member_name" text not null,
    "meeting_date" date not null,
    "meeting_location" text not null,
    "member_capacity" text not null,
    "procedure_reference" text,
    "associated_committee_or_delegation_code" text,
    "associated_committee_or_delegation_name" text
);


create table "public"."meps" (
    "id" text not null,
    "type" text not null,
    "label" text not null,
    "family_name" text not null,
    "given_name" text not null,
    "sort_label" text not null,
    "country_of_representation" text not null,
    "political_group" text not null,
    "official_family_name" text,
    "official_given_name" text
);


create table "public"."scheduled_job_runs" (
    "name" character varying(255) not null,
    "last_run_at" timestamp without time zone
);


alter sequence "public"."ep_meetings_id_seq" owned by "public"."ep_meetings"."id";

CREATE UNIQUE INDEX austrian_parliament_meetings_pkey ON public.austrian_parliament_meetings USING btree (id);

CREATE UNIQUE INDEX bt_documents_pkey ON public.bt_documents USING btree (id);

CREATE UNIQUE INDEX bt_plenarprotokolle_pkey ON public.bt_plenarprotokolle USING btree (id);

CREATE INDEX documents_embeddings_embedding_idx ON public.documents_embeddings USING ivfflat (embedding) WITH (lists='100');

CREATE UNIQUE INDEX documents_embeddings_pkey ON public.documents_embeddings USING btree (id);

CREATE UNIQUE INDEX ep_meetings_pkey ON public.ep_meetings USING btree (id);

CREATE UNIQUE INDEX ipex_events_pkey ON public.ipex_events USING btree (id);

CREATE UNIQUE INDEX legislative_files_pkey ON public.legislative_files USING btree (reference);

CREATE UNIQUE INDEX mep_meeting_attendee_mapping_pkey ON public.mep_meeting_attendee_mapping USING btree (meeting_id, attendee_id);

CREATE UNIQUE INDEX mep_meeting_attendees_pkey ON public.mep_meeting_attendees USING btree (id);

CREATE UNIQUE INDEX mep_meeting_attendees_transparency_register_url_key ON public.mep_meeting_attendees USING btree (transparency_register_url);

CREATE UNIQUE INDEX mep_meetings_pkey ON public.mep_meetings USING btree (id);

CREATE UNIQUE INDEX meps_pkey ON public.meps USING btree (id);

CREATE UNIQUE INDEX no_duplicates ON public.documents_embeddings USING btree (source_table, source_id, content_text);

CREATE UNIQUE INDEX scheduled_job_runs_pkey ON public.scheduled_job_runs USING btree (name);

alter table "public"."austrian_parliament_meetings" add constraint "austrian_parliament_meetings_pkey" PRIMARY KEY using index "austrian_parliament_meetings_pkey";

alter table "public"."bt_documents" add constraint "bt_documents_pkey" PRIMARY KEY using index "bt_documents_pkey";

alter table "public"."bt_plenarprotokolle" add constraint "bt_plenarprotokolle_pkey" PRIMARY KEY using index "bt_plenarprotokolle_pkey";

alter table "public"."documents_embeddings" add constraint "documents_embeddings_pkey" PRIMARY KEY using index "documents_embeddings_pkey";

alter table "public"."ep_meetings" add constraint "ep_meetings_pkey" PRIMARY KEY using index "ep_meetings_pkey";

alter table "public"."ipex_events" add constraint "ipex_events_pkey" PRIMARY KEY using index "ipex_events_pkey";

alter table "public"."legislative_files" add constraint "legislative_files_pkey" PRIMARY KEY using index "legislative_files_pkey";

alter table "public"."mep_meeting_attendee_mapping" add constraint "mep_meeting_attendee_mapping_pkey" PRIMARY KEY using index "mep_meeting_attendee_mapping_pkey";

alter table "public"."mep_meeting_attendees" add constraint "mep_meeting_attendees_pkey" PRIMARY KEY using index "mep_meeting_attendees_pkey";

alter table "public"."mep_meetings" add constraint "mep_meetings_pkey" PRIMARY KEY using index "mep_meetings_pkey";

alter table "public"."meps" add constraint "meps_pkey" PRIMARY KEY using index "meps_pkey";

alter table "public"."scheduled_job_runs" add constraint "scheduled_job_runs_pkey" PRIMARY KEY using index "scheduled_job_runs_pkey";

alter table "public"."documents_embeddings" add constraint "no_duplicates" UNIQUE using index "no_duplicates";

alter table "public"."mep_meeting_attendee_mapping" add constraint "mep_meeting_attendee_mapping_attendee_id_fkey" FOREIGN KEY (attendee_id) REFERENCES mep_meeting_attendees(id) ON DELETE CASCADE not valid;

alter table "public"."mep_meeting_attendee_mapping" validate constraint "mep_meeting_attendee_mapping_attendee_id_fkey";

alter table "public"."mep_meeting_attendee_mapping" add constraint "mep_meeting_attendee_mapping_meeting_id_fkey" FOREIGN KEY (meeting_id) REFERENCES mep_meetings(id) ON DELETE CASCADE not valid;

alter table "public"."mep_meeting_attendee_mapping" validate constraint "mep_meeting_attendee_mapping_meeting_id_fkey";

alter table "public"."mep_meeting_attendees" add constraint "mep_meeting_attendees_transparency_register_url_key" UNIQUE using index "mep_meeting_attendees_transparency_register_url_key";

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

grant delete on table "public"."austrian_parliament_meetings" to "anon";

grant insert on table "public"."austrian_parliament_meetings" to "anon";

grant references on table "public"."austrian_parliament_meetings" to "anon";

grant select on table "public"."austrian_parliament_meetings" to "anon";

grant trigger on table "public"."austrian_parliament_meetings" to "anon";

grant truncate on table "public"."austrian_parliament_meetings" to "anon";

grant update on table "public"."austrian_parliament_meetings" to "anon";

grant delete on table "public"."austrian_parliament_meetings" to "authenticated";

grant insert on table "public"."austrian_parliament_meetings" to "authenticated";

grant references on table "public"."austrian_parliament_meetings" to "authenticated";

grant select on table "public"."austrian_parliament_meetings" to "authenticated";

grant trigger on table "public"."austrian_parliament_meetings" to "authenticated";

grant truncate on table "public"."austrian_parliament_meetings" to "authenticated";

grant update on table "public"."austrian_parliament_meetings" to "authenticated";

grant delete on table "public"."austrian_parliament_meetings" to "service_role";

grant insert on table "public"."austrian_parliament_meetings" to "service_role";

grant references on table "public"."austrian_parliament_meetings" to "service_role";

grant select on table "public"."austrian_parliament_meetings" to "service_role";

grant trigger on table "public"."austrian_parliament_meetings" to "service_role";

grant truncate on table "public"."austrian_parliament_meetings" to "service_role";

grant update on table "public"."austrian_parliament_meetings" to "service_role";

grant delete on table "public"."bt_documents" to "anon";

grant insert on table "public"."bt_documents" to "anon";

grant references on table "public"."bt_documents" to "anon";

grant select on table "public"."bt_documents" to "anon";

grant trigger on table "public"."bt_documents" to "anon";

grant truncate on table "public"."bt_documents" to "anon";

grant update on table "public"."bt_documents" to "anon";

grant delete on table "public"."bt_documents" to "authenticated";

grant insert on table "public"."bt_documents" to "authenticated";

grant references on table "public"."bt_documents" to "authenticated";

grant select on table "public"."bt_documents" to "authenticated";

grant trigger on table "public"."bt_documents" to "authenticated";

grant truncate on table "public"."bt_documents" to "authenticated";

grant update on table "public"."bt_documents" to "authenticated";

grant delete on table "public"."bt_documents" to "service_role";

grant insert on table "public"."bt_documents" to "service_role";

grant references on table "public"."bt_documents" to "service_role";

grant select on table "public"."bt_documents" to "service_role";

grant trigger on table "public"."bt_documents" to "service_role";

grant truncate on table "public"."bt_documents" to "service_role";

grant update on table "public"."bt_documents" to "service_role";

grant delete on table "public"."bt_plenarprotokolle" to "anon";

grant insert on table "public"."bt_plenarprotokolle" to "anon";

grant references on table "public"."bt_plenarprotokolle" to "anon";

grant select on table "public"."bt_plenarprotokolle" to "anon";

grant trigger on table "public"."bt_plenarprotokolle" to "anon";

grant truncate on table "public"."bt_plenarprotokolle" to "anon";

grant update on table "public"."bt_plenarprotokolle" to "anon";

grant delete on table "public"."bt_plenarprotokolle" to "authenticated";

grant insert on table "public"."bt_plenarprotokolle" to "authenticated";

grant references on table "public"."bt_plenarprotokolle" to "authenticated";

grant select on table "public"."bt_plenarprotokolle" to "authenticated";

grant trigger on table "public"."bt_plenarprotokolle" to "authenticated";

grant truncate on table "public"."bt_plenarprotokolle" to "authenticated";

grant update on table "public"."bt_plenarprotokolle" to "authenticated";

grant delete on table "public"."bt_plenarprotokolle" to "service_role";

grant insert on table "public"."bt_plenarprotokolle" to "service_role";

grant references on table "public"."bt_plenarprotokolle" to "service_role";

grant select on table "public"."bt_plenarprotokolle" to "service_role";

grant trigger on table "public"."bt_plenarprotokolle" to "service_role";

grant truncate on table "public"."bt_plenarprotokolle" to "service_role";

grant update on table "public"."bt_plenarprotokolle" to "service_role";

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

grant delete on table "public"."ep_meetings" to "anon";

grant insert on table "public"."ep_meetings" to "anon";

grant references on table "public"."ep_meetings" to "anon";

grant select on table "public"."ep_meetings" to "anon";

grant trigger on table "public"."ep_meetings" to "anon";

grant truncate on table "public"."ep_meetings" to "anon";

grant update on table "public"."ep_meetings" to "anon";

grant delete on table "public"."ep_meetings" to "authenticated";

grant insert on table "public"."ep_meetings" to "authenticated";

grant references on table "public"."ep_meetings" to "authenticated";

grant select on table "public"."ep_meetings" to "authenticated";

grant trigger on table "public"."ep_meetings" to "authenticated";

grant truncate on table "public"."ep_meetings" to "authenticated";

grant update on table "public"."ep_meetings" to "authenticated";

grant delete on table "public"."ep_meetings" to "service_role";

grant insert on table "public"."ep_meetings" to "service_role";

grant references on table "public"."ep_meetings" to "service_role";

grant select on table "public"."ep_meetings" to "service_role";

grant trigger on table "public"."ep_meetings" to "service_role";

grant truncate on table "public"."ep_meetings" to "service_role";

grant update on table "public"."ep_meetings" to "service_role";

grant delete on table "public"."ipex_events" to "anon";

grant insert on table "public"."ipex_events" to "anon";

grant references on table "public"."ipex_events" to "anon";

grant select on table "public"."ipex_events" to "anon";

grant trigger on table "public"."ipex_events" to "anon";

grant truncate on table "public"."ipex_events" to "anon";

grant update on table "public"."ipex_events" to "anon";

grant delete on table "public"."ipex_events" to "authenticated";

grant insert on table "public"."ipex_events" to "authenticated";

grant references on table "public"."ipex_events" to "authenticated";

grant select on table "public"."ipex_events" to "authenticated";

grant trigger on table "public"."ipex_events" to "authenticated";

grant truncate on table "public"."ipex_events" to "authenticated";

grant update on table "public"."ipex_events" to "authenticated";

grant delete on table "public"."ipex_events" to "service_role";

grant insert on table "public"."ipex_events" to "service_role";

grant references on table "public"."ipex_events" to "service_role";

grant select on table "public"."ipex_events" to "service_role";

grant trigger on table "public"."ipex_events" to "service_role";

grant truncate on table "public"."ipex_events" to "service_role";

grant update on table "public"."ipex_events" to "service_role";

grant delete on table "public"."legislative_files" to "anon";

grant insert on table "public"."legislative_files" to "anon";

grant references on table "public"."legislative_files" to "anon";

grant select on table "public"."legislative_files" to "anon";

grant trigger on table "public"."legislative_files" to "anon";

grant truncate on table "public"."legislative_files" to "anon";

grant update on table "public"."legislative_files" to "anon";

grant delete on table "public"."legislative_files" to "authenticated";

grant insert on table "public"."legislative_files" to "authenticated";

grant references on table "public"."legislative_files" to "authenticated";

grant select on table "public"."legislative_files" to "authenticated";

grant trigger on table "public"."legislative_files" to "authenticated";

grant truncate on table "public"."legislative_files" to "authenticated";

grant update on table "public"."legislative_files" to "authenticated";

grant delete on table "public"."legislative_files" to "service_role";

grant insert on table "public"."legislative_files" to "service_role";

grant references on table "public"."legislative_files" to "service_role";

grant select on table "public"."legislative_files" to "service_role";

grant trigger on table "public"."legislative_files" to "service_role";

grant truncate on table "public"."legislative_files" to "service_role";

grant update on table "public"."legislative_files" to "service_role";

grant delete on table "public"."mep_meeting_attendee_mapping" to "anon";

grant insert on table "public"."mep_meeting_attendee_mapping" to "anon";

grant references on table "public"."mep_meeting_attendee_mapping" to "anon";

grant select on table "public"."mep_meeting_attendee_mapping" to "anon";

grant trigger on table "public"."mep_meeting_attendee_mapping" to "anon";

grant truncate on table "public"."mep_meeting_attendee_mapping" to "anon";

grant update on table "public"."mep_meeting_attendee_mapping" to "anon";

grant delete on table "public"."mep_meeting_attendee_mapping" to "authenticated";

grant insert on table "public"."mep_meeting_attendee_mapping" to "authenticated";

grant references on table "public"."mep_meeting_attendee_mapping" to "authenticated";

grant select on table "public"."mep_meeting_attendee_mapping" to "authenticated";

grant trigger on table "public"."mep_meeting_attendee_mapping" to "authenticated";

grant truncate on table "public"."mep_meeting_attendee_mapping" to "authenticated";

grant update on table "public"."mep_meeting_attendee_mapping" to "authenticated";

grant delete on table "public"."mep_meeting_attendee_mapping" to "service_role";

grant insert on table "public"."mep_meeting_attendee_mapping" to "service_role";

grant references on table "public"."mep_meeting_attendee_mapping" to "service_role";

grant select on table "public"."mep_meeting_attendee_mapping" to "service_role";

grant trigger on table "public"."mep_meeting_attendee_mapping" to "service_role";

grant truncate on table "public"."mep_meeting_attendee_mapping" to "service_role";

grant update on table "public"."mep_meeting_attendee_mapping" to "service_role";

grant delete on table "public"."mep_meeting_attendees" to "anon";

grant insert on table "public"."mep_meeting_attendees" to "anon";

grant references on table "public"."mep_meeting_attendees" to "anon";

grant select on table "public"."mep_meeting_attendees" to "anon";

grant trigger on table "public"."mep_meeting_attendees" to "anon";

grant truncate on table "public"."mep_meeting_attendees" to "anon";

grant update on table "public"."mep_meeting_attendees" to "anon";

grant delete on table "public"."mep_meeting_attendees" to "authenticated";

grant insert on table "public"."mep_meeting_attendees" to "authenticated";

grant references on table "public"."mep_meeting_attendees" to "authenticated";

grant select on table "public"."mep_meeting_attendees" to "authenticated";

grant trigger on table "public"."mep_meeting_attendees" to "authenticated";

grant truncate on table "public"."mep_meeting_attendees" to "authenticated";

grant update on table "public"."mep_meeting_attendees" to "authenticated";

grant delete on table "public"."mep_meeting_attendees" to "service_role";

grant insert on table "public"."mep_meeting_attendees" to "service_role";

grant references on table "public"."mep_meeting_attendees" to "service_role";

grant select on table "public"."mep_meeting_attendees" to "service_role";

grant trigger on table "public"."mep_meeting_attendees" to "service_role";

grant truncate on table "public"."mep_meeting_attendees" to "service_role";

grant update on table "public"."mep_meeting_attendees" to "service_role";

grant delete on table "public"."mep_meetings" to "anon";

grant insert on table "public"."mep_meetings" to "anon";

grant references on table "public"."mep_meetings" to "anon";

grant select on table "public"."mep_meetings" to "anon";

grant trigger on table "public"."mep_meetings" to "anon";

grant truncate on table "public"."mep_meetings" to "anon";

grant update on table "public"."mep_meetings" to "anon";

grant delete on table "public"."mep_meetings" to "authenticated";

grant insert on table "public"."mep_meetings" to "authenticated";

grant references on table "public"."mep_meetings" to "authenticated";

grant select on table "public"."mep_meetings" to "authenticated";

grant trigger on table "public"."mep_meetings" to "authenticated";

grant truncate on table "public"."mep_meetings" to "authenticated";

grant update on table "public"."mep_meetings" to "authenticated";

grant delete on table "public"."mep_meetings" to "service_role";

grant insert on table "public"."mep_meetings" to "service_role";

grant references on table "public"."mep_meetings" to "service_role";

grant select on table "public"."mep_meetings" to "service_role";

grant trigger on table "public"."mep_meetings" to "service_role";

grant truncate on table "public"."mep_meetings" to "service_role";

grant update on table "public"."mep_meetings" to "service_role";

grant delete on table "public"."meps" to "anon";

grant insert on table "public"."meps" to "anon";

grant references on table "public"."meps" to "anon";

grant select on table "public"."meps" to "anon";

grant trigger on table "public"."meps" to "anon";

grant truncate on table "public"."meps" to "anon";

grant update on table "public"."meps" to "anon";

grant delete on table "public"."meps" to "authenticated";

grant insert on table "public"."meps" to "authenticated";

grant references on table "public"."meps" to "authenticated";

grant select on table "public"."meps" to "authenticated";

grant trigger on table "public"."meps" to "authenticated";

grant truncate on table "public"."meps" to "authenticated";

grant update on table "public"."meps" to "authenticated";

grant delete on table "public"."meps" to "service_role";

grant insert on table "public"."meps" to "service_role";

grant references on table "public"."meps" to "service_role";

grant select on table "public"."meps" to "service_role";

grant trigger on table "public"."meps" to "service_role";

grant truncate on table "public"."meps" to "service_role";

grant update on table "public"."meps" to "service_role";

grant delete on table "public"."scheduled_job_runs" to "anon";

grant insert on table "public"."scheduled_job_runs" to "anon";

grant references on table "public"."scheduled_job_runs" to "anon";

grant select on table "public"."scheduled_job_runs" to "anon";

grant trigger on table "public"."scheduled_job_runs" to "anon";

grant truncate on table "public"."scheduled_job_runs" to "anon";

grant update on table "public"."scheduled_job_runs" to "anon";

grant delete on table "public"."scheduled_job_runs" to "authenticated";

grant insert on table "public"."scheduled_job_runs" to "authenticated";

grant references on table "public"."scheduled_job_runs" to "authenticated";

grant select on table "public"."scheduled_job_runs" to "authenticated";

grant trigger on table "public"."scheduled_job_runs" to "authenticated";

grant truncate on table "public"."scheduled_job_runs" to "authenticated";

grant update on table "public"."scheduled_job_runs" to "authenticated";

grant delete on table "public"."scheduled_job_runs" to "service_role";

grant insert on table "public"."scheduled_job_runs" to "service_role";

grant references on table "public"."scheduled_job_runs" to "service_role";

grant select on table "public"."scheduled_job_runs" to "service_role";

grant trigger on table "public"."scheduled_job_runs" to "service_role";

grant truncate on table "public"."scheduled_job_runs" to "service_role";

grant update on table "public"."scheduled_job_runs" to "service_role";


