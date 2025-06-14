alter table "public"."tweets" drop column "embedding_input";

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
            p.scraped_at
           FROM polish_presidency_meeting p
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
    base_with_topic.scraped_at,
    base_with_topic.location,
    base_with_topic.topic
   FROM base_with_topic;



