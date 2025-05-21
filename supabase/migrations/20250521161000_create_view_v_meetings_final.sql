-- +supabase_up
CREATE OR REPLACE VIEW public.v_meetings AS

-- -------- 1. mep_meetings ----------
SELECT
    m.id::text || '_mep_meetings'         AS meeting_id,
        m.id::text                            AS source_id,
        'mep_meetings'                        AS source_table,
    NOW()                                 AS scraped_at,
    NULL::timestamptz                     AS created_at,
        NULL::timestamptz                     AS updated_at,

        m.title                               AS title,
    m.meeting_date::timestamptz           AS meeting_start_datetime,
        NULL::timestamptz                     AS meeting_end_datetime,
        m.meeting_location                    AS location,
    NULL::text                            AS description,
        NULL::text                            AS meeting_url,
        NULL::text                            AS status,
        NULL::text                            AS source_url,
        NULL::text[]                          AS tags
FROM   public.mep_meetings m

UNION ALL

-- -------- 2. ep_meetings ----------
SELECT
    e.id::text || '_ep_meetings',
        e.id::text,
        'ep_meetings',
    NOW(),
    NULL::timestamptz,
        NULL::timestamptz,

        e.title,
    e.datetime AT TIME ZONE 'UTC',
    NULL::timestamptz,
        e.place,
    e.subtitles,
    NULL::text,
        NULL::text,
        NULL::text,
        NULL::text[]
FROM   public.ep_meetings e

/* Unavailable for now, commented out. --START block comment for IPEX events !!
UNION ALL

 ---------- 3. ipex_events ----------
SELECT
    i.id || '_ipex_events',
    i.id,
    'ipex_events',
    NOW(),
    NULL::timestamptz,
    NULL::timestamptz,

    i.title,
    i.start_date::timestamptz,
    i.end_date::timestamptz,
    i.meeting_location,
    NULL::text,
    NULL::text,
    NULL::text,
    NULL::text,
    i.tags
FROM   public.ipex_events i

UNION ALL
*/ --END block comment for IPEX events !!

---------- 4. austrian_parliament_meetings ----------
/* Unavailable for now, commented out. --START block comment for austrian_parliament_meetings events !!
SELECT
    a.id::text || '_austrian_parliament_meetings',
    a.id::text,
    'austrian_parliament_meetings',
    NOW(),
    NULL::timestamptz,
    NULL::timestamptz,

    a.title,
    a.meeting_date::timestamptz,
    NULL::timestamptz,
    a.meeting_location,
    NULL::text,
    a.meeting_url,
    NULL::text,
    NULL::text,
    NULL::text[]
FROM   public.austrian_parliament_meetings a
*/ --END block comment for IPEX events !!


GRANT SELECT ON public.v_meetings TO anon, authenticated, service_role;

-- +supabase_down
DROP VIEW IF EXISTS public.v_meetings;