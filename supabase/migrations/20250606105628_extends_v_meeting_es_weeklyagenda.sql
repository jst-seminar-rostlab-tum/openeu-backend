-- 1. Add source table -> location mapping to country_map_meetings (spanish_commission_meetings, weeky_agenda)
insert into public.country_map_meetings (source_table, country, iso2) values
  ('weekly_agenda',                  'European Union', 'EU')
on conflict (source_table) do update
  set country = excluded.country,
      iso2    = excluded.iso2;

-- 2. Rebuild the view with the new schema (adding: spanish_commission_meetings, weeky_agenda)
drop view if exists public.v_meetings cascade;

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
        i.scraped_at                as scraped_at
    from public.ipex_events i

    union all

    -- Belgian Parliament meetings
    select
        b.id || '_belgian_parliament'   as meeting_id,
        b.id::text                      as source_id,
        'belgian_parliament_meetings'   as source_table,
        coalesce(b.title_en, b.title)   as title,
        b.meeting_date::timestamptz     as meeting_start_datetime,
        null::timestamptz               as meeting_end_datetime,
        b.location                      as exact_location,
        coalesce(b.description_en, b.description) as description,
        b.meeting_url                   as meeting_url,
        null::text                      as status,
        null::text                      as source_url,
        null::text[]                    as tags,
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
        p.scraped_at                          as scraped_at
    from public.polish_presidency_meeting p

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
        w.scraped_at                                 as scraped_at
    from public.weekly_agenda w

)

select
    base.*,
    cm.country as location
from base
join public.country_map_meetings as cm
    on base.source_table = cm.source_table;