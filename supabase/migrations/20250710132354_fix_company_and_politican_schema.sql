drop view if exists "public"."v_profiles";

alter table "public"."companies" alter column "company_size" set data type text using "company_size"::text;

alter table "public"."politicians" alter column "area_of_expertise" set default '{}'::text[];

alter table "public"."politicians" alter column "area_of_expertise" set data type text[] using "area_of_expertise"::text[];

create or replace view "public"."v_profiles" as  SELECT p.id,
    p.name,
    p.surname,
    p.user_type,
    p.countries,
    p.newsletter_frequency,
    p.embedding_input,
    p.embedding,
    row_to_json(c.*) AS company,
    row_to_json(pol.*) AS politician,
    array_remove(array_agg(DISTINCT top.topic_id), NULL::text) AS topic_ids
   FROM (((profiles p
     LEFT JOIN companies c ON ((p.company_id = c.id)))
     LEFT JOIN politicians pol ON ((p.politician_id = pol.id)))
     LEFT JOIN profiles_to_topics top ON ((p.id = top.profile_id)))
  GROUP BY p.id, p.name, p.surname, p.user_type, p.countries, p.newsletter_frequency, p.embedding_input, p.embedding, c.id, pol.id;



