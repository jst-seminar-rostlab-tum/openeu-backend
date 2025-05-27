drop view if exists "public"."v_meetings";

alter table "public"."austrian_parliament_meetings" add column "embedding_input" text not null;

alter table "public"."austrian_parliament_meetings" add column "scraped_at" timestamp with time zone not null;

alter table "public"."austrian_parliament_meetings" alter column "id" drop default;

alter table "public"."austrian_parliament_meetings" alter column "id" set data type text using "id"::text;

create or replace view "public"."v_meetings" as  SELECT ((m.id)::text || '_mep_meetings'::text) AS meeting_id,
    (m.id)::text AS source_id,
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
 SELECT ((e.id)::text || '_ep_meetings'::text) AS meeting_id,
    (e.id)::text AS source_id,
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



