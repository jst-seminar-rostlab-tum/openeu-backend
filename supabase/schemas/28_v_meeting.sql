CREATE or REPLACE VIEW public.v_meetings as
with base as (
    -- MEP meetings
    select
        m.id || '_mep_meetings'      as meeting_id, 
        m.id                         as source_id,
        'mep_meetings'               as source_table,
        m.title                      as title,
        m.meeting_date::timestamptz  as meeting_start_datetime,
        null::timestamptz            as meeting_end_datetime,
        m.meeting_location           as exact_location,
        null::text                   as description,
        null::text                   as meeting_url,
        null::text                   as status,
        null::text                   as source_url,
        null::text[]                 as tags,
        (
            SELECT row_to_json(p) FROM public.meps p
            WHERE (
                -- meps.label: Firstname LASTNAME; member_name: LASTNAME Firstname
                (upper(p.family_name)|| ' ' || p.given_name ) = m.member_name
            )
            LIMIT 1
        ) as member,
        (
            SELECT string_agg(attendees.name, ';')
            FROM mep_meeting_attendee_mapping mapping
            JOIN mep_meeting_attendees attendees ON mapping.attendee_id = attendees.id
            WHERE mapping.meeting_id = m.id
        ) as attendees,
        m.scraped_at                 as scraped_at
    from public.mep_meetings m

    union all

    -- EP meetings
    select
        e.id || '_ep_meetings'       as meeting_id,
        e.id                         as source_id,
        'ep_meetings'                as source_table,
        e.title                      as title,
        (e.datetime at time zone 'UTC')::timestamptz as meeting_start_datetime,
        null::timestamptz            as meeting_end_datetime,
        e.place                      as exact_location,
        e.subtitles                  as description,
        null::text                   as meeting_url,
        null::text                   as status,
        null::text                   as source_url,
        null::text[]                 as tags,
        null::json                   as member,
        null::text                   as attendees,
        e.scraped_at                 as scraped_at
    from public.ep_meetings e

    union all

    -- Austrian Parliament meetings
    select
        a.id || '_austrian_parliament' as meeting_id,
        a.id::text                     as source_id,
        'austrian_parliament_meetings' as source_table,
        a.title                        as title,
        a.meeting_date::timestamptz    as meeting_start_datetime,
        null::timestamptz              as meeting_end_datetime,
        a.meeting_location             as exact_location,
        a.title_de                     as description,
        a.meeting_url                  as meeting_url,
        null::text                     as status,
        null::text                     as source_url,
        null::text[]                   as tags,
        null::json                     as member,
        null::text                     as attendees,
        a.scraped_at                   as scraped_at
    from public.austrian_parliament_meetings a

    union all

    -- IPEX events
    select
        i.id || '_ipex_events'      as meeting_id,
        i.id                        as source_id,
        'ipex_events'               as source_table,
        i.title                     as title,
        i.start_date::timestamptz   as meeting_start_datetime,
        i.end_date::timestamptz     as meeting_end_datetime,
        i.meeting_location          as exact_location,
        null::text                  as description,
        null::text                  as meeting_url,
        null::text                  as status,
        null::text                  as source_url,
        i.tags                      as tags,
        null::json                  as member,
        null::text                  as attendees,
        i.scraped_at                as scraped_at
    from public.ipex_events i

    union all

    -- Belgian Parliament meetings
    select
        b.id || '_belgian_parliament'   as meeting_id,
        b.id::text                      as source_id,
        'belgian_parliament_meetings'   as source_table,
        coalesce(b.title_en, b.title)   as title,
        b.meeting_date::timestamptz as meeting_start_datetime,
        null::timestamptz               as meeting_end_datetime,
        b.location                      as exact_location,
        coalesce(b.description_en, b.description) as description,
        b.meeting_url                   as meeting_url,
        null::text                      as status,
        null::text                      as source_url,
        null::text[]                    as tags,
        null::json                      as member,
        null::text                      as attendees,
        b.scraped_at                    as scraped_at
    from public.belgian_parliament_meetings b

    union all

    -- MEC Prep-Bodies meetings
    select
        p.id || '_mec_prep_bodies'        as meeting_id,
        p.id::text                        as source_id,
        'mec_prep_bodies_meeting'         as source_table,
        p.title                           as title,
        (p.meeting_timestamp at time zone 'UTC')::timestamptz
                                          as meeting_start_datetime,
        null::timestamptz                 as meeting_end_datetime,
        p.meeting_location                as exact_location,
        null::text                        as description,
        p.url                             as meeting_url,
        null::text                        as status,
        null::text                        as source_url,
        null::text[]                      as tags,
        null::json                        as member,
        null::text                        as attendees,
        p.scraped_at                      as scraped_at
    from public.mec_prep_bodies_meeting p

    union all

    -- MEC Summit / Ministerial meetings
    select
        s.id || '_mec_summit_ministerial'       as meeting_id,
        s.id::text                              as source_id,
        'mec_summit_ministerial_meeting'        as source_table,
        s.title                                 as title,
        s.meeting_date::timestamptz             as meeting_start_datetime,
        s.meeting_end_date::timestamptz         as meeting_end_datetime,
        null::text                              as exact_location,
        s.category_abbr                         as description,
        s.url                                   as meeting_url,
        null::text                              as status,
        null::text                              as source_url,
        null::text[]                            as tags,
        null::json                              as member,
        null::text                              as attendees,
        s.scraped_at                            as scraped_at
    from public.mec_summit_ministerial_meeting s

    union all

    -- Polish Presidency meetings
    select
        p.id || '_polish_presidency'          as meeting_id,
        p.id::text                            as source_id,
        'polish_presidency_meeting'           as source_table,
        p.title                               as title,
        p.meeting_date::timestamptz           as meeting_start_datetime,
        p.meeting_end_date::timestamptz       as meeting_end_datetime,
        p.meeting_location                    as exact_location,
        null::text                            as description,
        p.meeting_url                         as meeting_url,
        null::text                            as status,
        null::text                            as source_url,
        null::text[]                          as tags,
        null::json                            as member,
        null::text                            as attendees,
        p.scraped_at                          as scraped_at
    from public.polish_presidency_meeting p

    union all

    -- Spanish Commission meetings
    select
        s.id || '_spanish_commission'              AS meeting_id,
        s.id                                       AS source_id,
        'spanish_commission_meetings'              AS source_table,
        coalesce(s.title_en, s.title)              AS title,
        (
            s.date +
            COALESCE(
            -- Extract time if it matches 'HH:MM' at the start (with optional space, period, or 'h.')
            (
                CASE
                WHEN s.time IS NULL OR trim(s.time) = '' OR lower(trim(s.time)) = 'empty'
                    THEN NULL
                WHEN trim(s.time) ~ '^(\d{1,2}:\d{2})'
                    THEN substring(trim(s.time) FROM '^(\d{1,2}:\d{2})')::time
                ELSE NULL
                END
            ),
            '00:00'::time
            )
        )::timestamptz                             AS meeting_start_datetime,
        NULL::timestamptz                          AS meeting_end_datetime,
        coalesce(s.location_en, s.location)        AS exact_location,
        coalesce(s.description_en, s.description)  AS description,
        s.url                                      AS meeting_url,
        NULL::text                                 AS status,
        NULL::text                                 AS source_url,
        NULL::text[]                               AS tags,
        null::json                                 AS member,
        null::text                                 AS attendees,
        s.scraped_at                               AS scraped_at
    from public.spanish_commission_meetings s


    union all

    -- Weekly agenda (EP generic calendar)
    select
        w.id || '_weekly_agenda'                     as meeting_id,
        w.id                                         as source_id,
        'weekly_agenda'                              as source_table,
        w.title                                      as title,
        -- build timestamptz from date + parsed start, fallback to time = 00:00 if no time provided
        ( w.date
          + coalesce(
                CASE
                    WHEN w.time IS NULL THEN NULL
                    WHEN strpos(w.time, '-')  > 0 THEN trim(split_part(w.time, '-', 1))::time
                    ELSE trim(w.time)::time
                END
            , '00:00'::time)
        )                                            ::timestamptz as meeting_start_datetime,
        -- build timestamptz from date + parsed end (or NULL), adding 1 day when end < start
        CASE
        WHEN strpos(w.time, '-') > 0 THEN
        (
            w.date
            + trim(split_part(w.time, '-', 2))::time
            + CASE
                WHEN trim(split_part(w.time, '-', 2))::time
                    < trim(split_part(w.time, '-', 1))::time
                THEN INTERVAL '1 day'
                ELSE INTERVAL '0'
            END
        )::timestamptz
        ELSE NULL
        END                                          as meeting_end_datetime,
        w.location                                   as exact_location,
        w.description                                as description,
        null::text                                   as meeting_url,
        null::text                                   as status,
        null::text                                   as source_url,
        array[w.type]::text[]                        as tags,
        null::json                                   as member,
        null::text                                   as attendees,
        w.scraped_at                                 as scraped_at
    from public.weekly_agenda w

    union all

    -- EC Res Inno Meetings
    select
        r.id || '_ec_res_inno_meetings'             as meeting_id,
        r.id                                         as source_id,
        'ec_res_inno_meetings'                      as source_table,
        r.title                                      as title,
        r.start_date::timestamptz                    as meeting_start_datetime,
        r.end_date::timestamptz                      as meeting_end_datetime,
        r.location                                   as exact_location,
        r.description                                as description,
        r.meeting_url                                as meeting_url,
        null::text                                   as status,
        null::text                                   as source_url,
        r.subjects                                   as tags,
        null::json                                   as member,
        null::text                                   as attendees,
        r.scraped_at                                 as scraped_at
    from public.ec_res_inno_meetings r

        union all

    -- NL Tweede Kamer (Dutch House of Representatives) meetings
    select
        n.id || '_nl_twka_meetings'                                        as meeting_id,
        n.id                                                               as source_id,
        'nl_twka_meetings'                                                 as source_table,
        coalesce(nullif(n.translated_title, ''), nullif(n.original_title, ''), n.title) 
                                                                           as title,
        n.start_datetime                                                   as meeting_start_datetime,
        n.end_datetime                                                     as meeting_end_datetime,
        n.location                                                         as exact_location,

        /* simple human-readable description built from meeting_type + commission */
        nullif(concat_ws(' | ',
                         nullif(n.meeting_type, ''),
                         nullif(n.commission, '')
        ), '')                                                             as description,

        n.link                                                             as meeting_url,
        null::text                                                         as status,
        null::text                                                         as source_url,

        /* tags: include meeting_type & commission when present */
        (
            select coalesce(array_agg(tag_txt), '{}')::text[]
            from unnest(array[
                    nullif(n.meeting_type, ''),
                    nullif(n.commission, '')
                 ]) as t(tag_txt)
            where tag_txt is not null
        )                                                                  as tags,
        n.ministers::json                                                  as member,

        /* flatten attendees JSONB (array of objs or strings) to semicolon-sep names */
        (
            select string_agg(
                case
                    when jsonb_typeof(elem) = 'object'
                        then coalesce(elem->>'name', elem->>'full_name')
                    else trim(both '"' from elem::text)
                end,
                ';'
            )
            from jsonb_array_elements(n.attendees) elem
        )                                                                  as attendees,

        n.scraped_at                                                       as scraped_at
    from public.nl_twka_meetings n

),
base_with_location AS (
    SELECT
        base.*,
        cm.country AS location
    FROM base
    JOIN public.country_map_meetings AS cm
        ON base.source_table = cm.source_table
),
base_with_topic AS (
    SELECT
        bwl.*,
        mt.topic AS topic
    FROM base_with_location bwl
    LEFT JOIN public.meeting_topic_assignments mta
        ON mta.source_id = bwl.source_id
        AND mta.source_table = bwl.source_table
    LEFT JOIN public.meeting_topics mt
        ON mt.id = mta.topic_id
)

SELECT * FROM base_with_topic;

CREATE OR REPLACE FUNCTION public.get_meetings_by_filter(
    source_tables text[],
    source_ids text[],
    max_results integer,
    start_date timestamp with time zone DEFAULT NULL,
    end_date timestamp with time zone DEFAULT NULL,
    country text DEFAULT NULL,
    topics text[] DEFAULT NULL
)
RETURNS SETOF v_meetings
LANGUAGE sql
AS $$
SELECT vm.*
FROM v_meetings vm
         JOIN unnest(source_tables, source_ids) AS src(source_table, source_id)
              ON vm.source_table = src.source_table
                  AND vm.source_id = src.source_id
WHERE (start_date IS NULL OR vm.meeting_start_datetime::date <= end_date::date)
  AND (end_date IS NULL OR COALESCE(vm.meeting_end_datetime, vm.meeting_start_datetime)::date >= start_date::date)
  AND (country IS NULL OR LOWER(vm.location) = LOWER(country))
  AND (topics IS NULL OR vm.topic = ANY(topics))
    LIMIT max_results;
$$;


-- ------------------------------------------------------------
-- Function: public.get_meeting_tables()
-- Description: returns all distinct source_table names in v_meetings
-- Usage (RPC): SELECT * FROM get_meeting_tables();
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION public.get_meeting_tables()
  RETURNS TABLE(source_table text)
  LANGUAGE sql
AS $$
  SELECT DISTINCT source_table
  FROM public.v_meetings
  ORDER BY source_table;
$$;
