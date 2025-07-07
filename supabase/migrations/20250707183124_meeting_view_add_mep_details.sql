drop function if exists "public"."get_meetings_by_filter";
drop view if exists "public"."v_meetings";

set check_function_bodies = off;

create or replace view "public"."v_meetings" as  WITH base AS (
         SELECT (m.id || '_mep_meetings'::text) AS meeting_id,
            m.id AS source_id,
            'mep_meetings'::text AS source_table,
            m.title,
            (m.meeting_date)::timestamp with time zone AS meeting_start_datetime,
            NULL::timestamp with time zone AS meeting_end_datetime,
            m.meeting_location AS exact_location,
            NULL::text AS description,
            NULL::text AS meeting_url,
            NULL::text AS status,
            NULL::text AS source_url,
            NULL::text[] AS tags,
            ( SELECT row_to_json(p.*) AS row_to_json
                   FROM meps p
                  WHERE (((upper(p.family_name) || ' '::text) || p.given_name) = m.member_name)
                 LIMIT 1) AS member,
            ( SELECT string_agg(attendees.name, ';'::text) AS string_agg
                   FROM (mep_meeting_attendee_mapping mapping
                     JOIN mep_meeting_attendees attendees ON ((mapping.attendee_id = attendees.id)))
                  WHERE (mapping.meeting_id = m.id)) AS attendees,
            m.scraped_at
           FROM mep_meetings m
        UNION ALL
         SELECT (e.id || '_ep_meetings'::text) AS meeting_id,
            e.id AS source_id,
            'ep_meetings'::text AS source_table,
            e.title,
            (e.datetime AT TIME ZONE 'UTC'::text) AS meeting_start_datetime,
            NULL::timestamp with time zone AS meeting_end_datetime,
            e.place AS exact_location,
            e.subtitles AS description,
            NULL::text AS meeting_url,
            NULL::text AS status,
            NULL::text AS source_url,
            NULL::text[] AS tags,
            NULL::json as member,
            NULL::text AS attendees,
            e.scraped_at
           FROM ep_meetings e
        UNION ALL
         SELECT (a.id || '_austrian_parliament'::text) AS meeting_id,
            a.id AS source_id,
            'austrian_parliament_meetings'::text AS source_table,
            a.title,
            (a.meeting_date)::timestamp with time zone AS meeting_start_datetime,
            NULL::timestamp with time zone AS meeting_end_datetime,
            a.meeting_location AS exact_location,
            a.title_de AS description,
            a.meeting_url,
            NULL::text AS status,
            NULL::text AS source_url,
            NULL::text[] AS tags,
            NULL::json as member,
            NULL::text AS attendees,
            a.scraped_at
           FROM austrian_parliament_meetings a
        UNION ALL
         SELECT (i.id || '_ipex_events'::text) AS meeting_id,
            i.id AS source_id,
            'ipex_events'::text AS source_table,
            i.title,
            (i.start_date)::timestamp with time zone AS meeting_start_datetime,
            (i.end_date)::timestamp with time zone AS meeting_end_datetime,
            i.meeting_location AS exact_location,
            NULL::text AS description,
            NULL::text AS meeting_url,
            NULL::text AS status,
            NULL::text AS source_url,
            i.tags,
            NULL::json as member,
            NULL::text AS attendees,
            i.scraped_at
           FROM ipex_events i
        UNION ALL
         SELECT (b.id || '_belgian_parliament'::text) AS meeting_id,
            b.id AS source_id,
            'belgian_parliament_meetings'::text AS source_table,
            COALESCE(b.title_en, b.title) AS title,
            (b.meeting_date)::timestamp with time zone AS meeting_start_datetime,
            NULL::timestamp with time zone AS meeting_end_datetime,
            b.location AS exact_location,
            COALESCE(b.description_en, b.description) AS description,
            b.meeting_url,
            NULL::text AS status,
            NULL::text AS source_url,
            NULL::text[] AS tags,
            NULL::json as member,
            NULL::text AS attendees,
            b.scraped_at
           FROM belgian_parliament_meetings b
        UNION ALL
         SELECT (p.id || '_mec_prep_bodies'::text) AS meeting_id,
            p.id AS source_id,
            'mec_prep_bodies_meeting'::text AS source_table,
            p.title,
            (p.meeting_timestamp AT TIME ZONE 'UTC'::text) AS meeting_start_datetime,
            NULL::timestamp with time zone AS meeting_end_datetime,
            p.meeting_location AS exact_location,
            NULL::text AS description,
            p.url AS meeting_url,
            NULL::text AS status,
            NULL::text AS source_url,
            NULL::text[] AS tags,
            NULL::json as member,
            NULL::text AS attendees,
            p.scraped_at
           FROM mec_prep_bodies_meeting p
        UNION ALL
         SELECT (s.id || '_mec_summit_ministerial'::text) AS meeting_id,
            s.id AS source_id,
            'mec_summit_ministerial_meeting'::text AS source_table,
            s.title,
            (s.meeting_date)::timestamp with time zone AS meeting_start_datetime,
            (s.meeting_end_date)::timestamp with time zone AS meeting_end_datetime,
            NULL::text AS exact_location,
            s.category_abbr AS description,
            s.url AS meeting_url,
            NULL::text AS status,
            NULL::text AS source_url,
            NULL::text[] AS tags,
            NULL::json as member,
            NULL::text AS attendees,
            s.scraped_at
           FROM mec_summit_ministerial_meeting s
        UNION ALL
         SELECT (p.id || '_polish_presidency'::text) AS meeting_id,
            p.id AS source_id,
            'polish_presidency_meeting'::text AS source_table,
            p.title,
            (p.meeting_date)::timestamp with time zone AS meeting_start_datetime,
            (p.meeting_end_date)::timestamp with time zone AS meeting_end_datetime,
            p.meeting_location AS exact_location,
            NULL::text AS description,
            p.meeting_url,
            NULL::text AS status,
            NULL::text AS source_url,
            NULL::text[] AS tags,
            NULL::json as member,
            NULL::text AS attendees,
            p.scraped_at
           FROM polish_presidency_meeting p
        UNION ALL
         SELECT (w.id || '_weekly_agenda'::text) AS meeting_id,
            w.id AS source_id,
            'weekly_agenda'::text AS source_table,
            w.title,
            ((w.date + COALESCE(
                CASE
                    WHEN (w."time" IS NULL) THEN NULL::time without time zone
                    WHEN (strpos(w."time", '-'::text) > 0) THEN (TRIM(BOTH FROM split_part(w."time", '-'::text, 1)))::time without time zone
                    ELSE (TRIM(BOTH FROM w."time"))::time without time zone
                END, '00:00:00'::time without time zone)))::timestamp with time zone AS meeting_start_datetime,
                CASE
                    WHEN (strpos(w."time", '-'::text) > 0) THEN (((w.date + (TRIM(BOTH FROM split_part(w."time", '-'::text, 2)))::time without time zone) +
                    CASE
                        WHEN ((TRIM(BOTH FROM split_part(w."time", '-'::text, 2)))::time without time zone < (TRIM(BOTH FROM split_part(w."time", '-'::text, 1)))::time without time zone) THEN '1 day'::interval
                        ELSE '00:00:00'::interval
                    END))::timestamp with time zone
                    ELSE NULL::timestamp with time zone
                END AS meeting_end_datetime,
            w.location AS exact_location,
            w.description,
            NULL::text AS meeting_url,
            NULL::text AS status,
            NULL::text AS source_url,
            ARRAY[w.type] AS tags,
            NULL::json as member,
            NULL::text AS attendees,
            w.scraped_at
           FROM weekly_agenda w
        ), base_with_location AS (
         SELECT base.meeting_id,
            base.source_id,
            base.source_table,
            base.title,
            base.meeting_start_datetime,
            base.meeting_end_datetime,
            base.exact_location,
            base.description,
            base.meeting_url,
            base.status,
            base.source_url,
            base.tags,
            base.member,
            base.attendees,
            base.scraped_at,
            cm.country AS location
           FROM (base
             JOIN country_map_meetings cm ON ((base.source_table = cm.source_table)))
        ), base_with_topic AS (
         SELECT bwl.meeting_id,
            bwl.source_id,
            bwl.source_table,
            bwl.title,
            bwl.meeting_start_datetime,
            bwl.meeting_end_datetime,
            bwl.exact_location,
            bwl.description,
            bwl.meeting_url,
            bwl.status,
            bwl.source_url,
            bwl.tags,
            bwl.member,
            bwl.attendees,
            bwl.scraped_at,
            bwl.location,
            mt.topic
           FROM ((base_with_location bwl
             LEFT JOIN meeting_topic_assignments mta ON (((mta.source_id = bwl.source_id) AND (mta.source_table = bwl.source_table))))
             LEFT JOIN meeting_topics mt ON ((mt.id = mta.topic_id)))
        )
 SELECT base_with_topic.meeting_id,
    base_with_topic.source_id,
    base_with_topic.source_table,
    base_with_topic.title,
    base_with_topic.meeting_start_datetime,
    base_with_topic.meeting_end_datetime,
    base_with_topic.exact_location,
    base_with_topic.description,
    base_with_topic.meeting_url,
    base_with_topic.status,
    base_with_topic.source_url,
    base_with_topic.tags,
    base_with_topic.member,
    base_with_topic.attendees,
    base_with_topic.scraped_at,
    base_with_topic.location,
    base_with_topic.topic
   FROM base_with_topic;

CREATE OR REPLACE FUNCTION public.get_meetings_by_filter(source_tables text[], source_ids text[], max_results integer, start_date timestamp with time zone DEFAULT NULL::timestamp with time zone, end_date timestamp with time zone DEFAULT NULL::timestamp with time zone, country text DEFAULT NULL::text, topics text[] DEFAULT NULL::text[])
 RETURNS SETOF v_meetings
 LANGUAGE sql
AS $function$
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
$function$
;