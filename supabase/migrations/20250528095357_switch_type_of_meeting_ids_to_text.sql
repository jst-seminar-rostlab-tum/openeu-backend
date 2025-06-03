drop view if exists "public"."v_meetings";
-- Drop foreign key constraints
alter table "public"."mep_meeting_attendee_mapping" 
    drop constraint if exists "mep_meeting_attendee_mapping_attendee_id_fkey",
    drop constraint if exists "mep_meeting_attendee_mapping_meeting_id_fkey";
-- First change the primary key columns
alter table "public"."documents_embeddings" alter column "id" set data type text using "id"::text;
alter table "public"."documents_embeddings" alter column "id" set default (gen_random_uuid())::text;
alter table "public"."ep_meetings" alter column "id" set data type text using "id"::text;
alter table "public"."ep_meetings" alter column "id" set default (gen_random_uuid())::text;
alter table "public"."mec_prep_bodies_meeting" alter column "id" set data type text using "id"::text;
alter table "public"."mec_prep_bodies_meeting" alter column "id" set default (gen_random_uuid())::text;
alter table "public"."mec_summit_ministerial_meeting" alter column "id" set data type text using "id"::text;
alter table "public"."mec_summit_ministerial_meeting" alter column "id" set default (gen_random_uuid())::text;
alter table "public"."mep_meeting_attendees" alter column "id" set data type text using "id"::text;
alter table "public"."mep_meeting_attendees" alter column "id" set default (gen_random_uuid())::text;
alter table "public"."mep_meetings" alter column "id" set data type text using "id"::text;
alter table "public"."mep_meetings" alter column "id" set default (gen_random_uuid())::text;
alter table "public"."weekly_agenda" alter column "id" set data type text using "id"::text;
alter table "public"."weekly_agenda" alter column "id" set default (gen_random_uuid())::text;
-- Then change the foreign key columns
alter table "public"."mep_meeting_attendee_mapping" alter column "attendee_id" set data type text using "attendee_id"::text;
alter table "public"."mep_meeting_attendee_mapping" alter column "meeting_id" set data type text using "meeting_id"::text;
-- Recreate foreign key constraints
alter table "public"."mep_meeting_attendee_mapping"
    add constraint "mep_meeting_attendee_mapping_attendee_id_fkey" 
    foreign key (attendee_id) references "public"."mep_meeting_attendees"(id) on delete cascade,
    add constraint "mep_meeting_attendee_mapping_meeting_id_fkey" 
    foreign key (meeting_id) references "public"."mep_meetings"(id) on delete cascade;
-- Drop sequences
drop sequence if exists "public"."ep_meetings_id_seq";
drop sequence if exists "public"."mec_summit_ministerial_meeting_id_seq";
drop sequence if exists "public"."weekly_agenda_id_seq";
-- Recreate the view
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
    NULL::text[] AS tags
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
    NULL::text[] AS tags
   FROM ep_meetings e
UNION ALL
 SELECT (a.id || '_austrian_parliament'::text) AS meeting_id,
    (a.id)::text AS source_id,
    'austrian_parliament_meetings'::text AS source_table,
    a.title,
    (a.meeting_date)::timestamp with time zone AS meeting_start_datetime,
    NULL::timestamp with time zone AS meeting_end_datetime,
    a.meeting_location AS location,
    a.title_de AS description,
    a.meeting_url,
    NULL::text AS status,
    NULL::text AS source_url,
    NULL::text[] AS tags
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
    i.tags
   FROM ipex_events i;
