	CREATE OR REPLACE VIEW public.v_meetings AS
	SELECT
        m.id::text || '_mep_meetings'         AS meeting_id,
	    m.id::text                            AS source_id,
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
	    e.id::text || '_ep_meetings'          AS meeting_id,
	    e.id::text                            AS source_id,
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
	FROM   public.ep_meetings e;
