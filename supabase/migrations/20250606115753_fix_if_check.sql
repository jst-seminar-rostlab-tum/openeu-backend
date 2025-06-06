revoke delete on table "public"."country_map_meetings" from "anon";

revoke insert on table "public"."country_map_meetings" from "anon";

revoke references on table "public"."country_map_meetings" from "anon";

revoke select on table "public"."country_map_meetings" from "anon";

revoke trigger on table "public"."country_map_meetings" from "anon";

revoke truncate on table "public"."country_map_meetings" from "anon";

revoke update on table "public"."country_map_meetings" from "anon";

revoke delete on table "public"."country_map_meetings" from "authenticated";

revoke insert on table "public"."country_map_meetings" from "authenticated";

revoke references on table "public"."country_map_meetings" from "authenticated";

revoke select on table "public"."country_map_meetings" from "authenticated";

revoke trigger on table "public"."country_map_meetings" from "authenticated";

revoke truncate on table "public"."country_map_meetings" from "authenticated";

revoke update on table "public"."country_map_meetings" from "authenticated";

revoke delete on table "public"."country_map_meetings" from "service_role";

revoke insert on table "public"."country_map_meetings" from "service_role";

revoke references on table "public"."country_map_meetings" from "service_role";

revoke select on table "public"."country_map_meetings" from "service_role";

revoke trigger on table "public"."country_map_meetings" from "service_role";

revoke truncate on table "public"."country_map_meetings" from "service_role";

revoke update on table "public"."country_map_meetings" from "service_role";

revoke delete on table "public"."notifications" from "anon";

revoke insert on table "public"."notifications" from "anon";

revoke references on table "public"."notifications" from "anon";

revoke select on table "public"."notifications" from "anon";

revoke trigger on table "public"."notifications" from "anon";

revoke truncate on table "public"."notifications" from "anon";

revoke update on table "public"."notifications" from "anon";

revoke delete on table "public"."notifications" from "authenticated";

revoke insert on table "public"."notifications" from "authenticated";

revoke references on table "public"."notifications" from "authenticated";

revoke select on table "public"."notifications" from "authenticated";

revoke trigger on table "public"."notifications" from "authenticated";

revoke truncate on table "public"."notifications" from "authenticated";

revoke update on table "public"."notifications" from "authenticated";

revoke delete on table "public"."notifications" from "service_role";

revoke insert on table "public"."notifications" from "service_role";

revoke references on table "public"."notifications" from "service_role";

revoke select on table "public"."notifications" from "service_role";

revoke trigger on table "public"."notifications" from "service_role";

revoke truncate on table "public"."notifications" from "service_role";

revoke update on table "public"."notifications" from "service_role";

alter table "public"."austrian_parliament_meetings" drop constraint "austrian_parliament_meetings_title_meeting_type_meeting_dat_key";

alter table "public"."notifications" drop constraint "notifications_user_id_fkey";

drop function if exists "public"."get_user_by_id"(uid uuid);

drop view if exists "public"."v_meetings";

alter table "public"."country_map_meetings" drop constraint "country_map_meetings_pkey";

alter table "public"."notifications" drop constraint "notifications_pkey";

alter table "public"."scheduled_job_runs" drop constraint "scheduled_job_runs_pkey";

drop index if exists "public"."austrian_parliament_meetings_title_meeting_type_meeting_dat_key";

drop index if exists "public"."country_map_meetings_pkey";

drop index if exists "public"."notifications_pkey";

drop index if exists "public"."scheduled_job_runs_pkey";

drop table "public"."country_map_meetings";

drop table "public"."notifications";

alter table "public"."austrian_parliament_meetings" alter column "id" drop default;

alter table "public"."scheduled_job_runs" drop column "error_msg";

alter table "public"."scheduled_job_runs" drop column "id";

alter table "public"."scheduled_job_runs" drop column "inserted_rows";

alter table "public"."scheduled_job_runs" drop column "success";

alter table "public"."scheduled_job_runs" alter column "last_run_at" drop default;

drop sequence if exists "public"."notifications_id_seq";

drop sequence if exists "public"."scheduled_job_runs_id_seq";

CREATE UNIQUE INDEX scheduled_job_runs_pkey ON public.scheduled_job_runs USING btree (name);

alter table "public"."scheduled_job_runs" add constraint "scheduled_job_runs_pkey" PRIMARY KEY using index "scheduled_job_runs_pkey";

create or replace view "public"."v_meetings" as  SELECT (m.id || '_mep_meetings'::text) AS meeting_id,
    m.id AS source_id,
    'mep_meetings'::text AS source_table,
    m.title,
    (m.meeting_date)::timestamp with time zone AS meeting_start_datetime,
    NULL::timestamp with time zone AS meeting_end_datetime,
    m.meeting_location AS location,
    NULL::text AS description,
    NULL::text AS meeting_url,
    NULL::text AS status,
    NULL::text AS source_url,
    NULL::text[] AS tags,
    m.scraped_at
   FROM mep_meetings m
UNION ALL
 SELECT (e.id || '_ep_meetings'::text) AS meeting_id,
    e.id AS source_id,
    'ep_meetings'::text AS source_table,
    e.title,
    (e.datetime AT TIME ZONE 'UTC'::text) AS meeting_start_datetime,
    NULL::timestamp with time zone AS meeting_end_datetime,
    e.place AS location,
    e.subtitles AS description,
    NULL::text AS meeting_url,
    NULL::text AS status,
    NULL::text AS source_url,
    NULL::text[] AS tags,
    e.scraped_at
   FROM ep_meetings e
UNION ALL
 SELECT (a.id || '_austrian_parliament'::text) AS meeting_id,
    a.id AS source_id,
    'austrian_parliament_meetings'::text AS source_table,
    a.title,
    (a.meeting_date)::timestamp with time zone AS meeting_start_datetime,
    NULL::timestamp with time zone AS meeting_end_datetime,
    a.meeting_location AS location,
    a.title_de AS description,
    a.meeting_url,
    NULL::text AS status,
    NULL::text AS source_url,
    NULL::text[] AS tags,
    a.scraped_at
   FROM austrian_parliament_meetings a
UNION ALL
 SELECT (i.id || '_ipex_events'::text) AS meeting_id,
    i.id AS source_id,
    'ipex_events'::text AS source_table,
    i.title,
    (i.start_date)::timestamp with time zone AS meeting_start_datetime,
    (i.end_date)::timestamp with time zone AS meeting_end_datetime,
    i.meeting_location AS location,
    NULL::text AS description,
    NULL::text AS meeting_url,
    NULL::text AS status,
    NULL::text AS source_url,
    i.tags,
    i.scraped_at
   FROM ipex_events i;



