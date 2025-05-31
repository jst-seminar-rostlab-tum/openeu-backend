	CREATE OR REPLACE VIEW public.v_meetings AS
	SELECT
        m.id || '_mep_meetings'         AS meeting_id,
	    m.id                            AS source_id,
	    'mep_meetings'                        AS source_table,
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
	SELECT
	    e.id || '_ep_meetings'          AS meeting_id,
	    e.id                            AS source_id,
	    'ep_meetings'                         AS source_table,
	    e.title                               AS title,
	    e.datetime AT TIME ZONE 'UTC'         AS meeting_start_datetime,
	    NULL::timestamptz                     AS meeting_end_datetime,
	    e.place                               AS location,
	    e.subtitles                           AS description,
	    NULL::text                            AS meeting_url,
	    NULL::text                            AS status,
	    NULL::text                            AS source_url,
	    NULL::text[]                          AS tags
	FROM   public.ep_meetings e
    UNION ALL

    -- Austrian Parliament Meetings
    SELECT
        a.id || '_austrian_parliament'  AS meeting_id,
        a.id::text                            AS source_id,
        'austrian_parliament_meetings'        AS source_table,
        a.title                               AS title,
        a.meeting_date::timestamptz           AS meeting_start_datetime,
        NULL::timestamptz                     AS meeting_end_datetime,
        a.meeting_location                    AS location,
        a.title_de                            AS description,
        a.meeting_url                         AS meeting_url,
        NULL::text                            AS status,
        NULL::text                            AS source_url,
        NULL::text[]                          AS tags
    FROM public.austrian_parliament_meetings a

    UNION ALL

    -- IPEX Events
    SELECT
        i.id || '_ipex_events'                AS meeting_id,
        i.id                                  AS source_id,
        'ipex_events'                         AS source_table,
        i.title                               AS title,
        i.start_date::timestamptz             AS meeting_start_datetime,
        i.end_date::timestamptz               AS meeting_end_datetime,
        i.meeting_location                    AS location,
        NULL::text                            AS description,
        NULL::text                            AS meeting_url,
        NULL::text                            AS status,
        NULL::text                            AS source_url,
        i.tags                                AS tags
    FROM public.ipex_events i;
