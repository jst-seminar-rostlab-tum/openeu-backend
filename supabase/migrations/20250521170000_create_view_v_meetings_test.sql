-- +supabase_up
CREATE OR REPLACE VIEW public.v_meetings AS

-- ---------- 1. mep_meetings ----------
SELECT
    m.id::text || '_mep_meetings' AS meeting_id,
        m.id::text                    AS source_id,
        'mep_meetings'                AS source_table,
    NOW()                         AS scraped_at,
    NULL::timestamptz             AS created_at,
        NULL::timestamptz             AS updated_at,
        m.title,
    m.meeting_date::timestamptz   AS meeting_start_datetime,
        NULL::timestamptz             AS meeting_end_datetime,
        m.meeting_location            AS location,
    NULL::text                    AS description,
        NULL::text                    AS meeting_url,
        NULL::text                    AS status,
        NULL::text                    AS source_url,
        NULL::text[]                  AS tags
FROM   public.mep_meetings m

UNION ALL

-- ---------- 2. ep_meetings ----------
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
FROM public.ep_meetings e
    GRANT SELECT ON public.v_meetings TO anon, authenticated, service_role
-- +supabase_down
DROP VIEW IF EXISTS public.v_meetings