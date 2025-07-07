drop view if exists "public"."v_profiles";

alter table "public"."profiles" add column "embedding_input" text not null;

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
    array_remove(array_agg(top.topic_id), NULL::text) AS topic_ids
   FROM (((profiles p
     LEFT JOIN companies c ON ((p.company_id = c.id)))
     LEFT JOIN politicians pol ON ((p.politician_id = pol.id)))
     LEFT JOIN profiles_to_topics top ON ((p.id = top.profile_id)))
  GROUP BY p.id, p.name, p.surname, p.user_type, p.countries, p.newsletter_frequency, p.embedding_input, p.embedding, c.id, pol.id;



