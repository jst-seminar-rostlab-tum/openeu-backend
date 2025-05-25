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
   FROM ep_meetings e;



