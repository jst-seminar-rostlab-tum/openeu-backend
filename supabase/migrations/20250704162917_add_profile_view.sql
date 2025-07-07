create or replace view "public"."v_profiles" as  SELECT p.id,
    p.name,
    p.surname,
    p.user_type,
    p.countries,
    p.newsletter_frequency,
    p.embedding,
    row_to_json(c.*) AS company,
    row_to_json(pol.*) AS politician,
    array_remove(array_agg(DISTINCT top.topic_id), NULL) AS topic_ids
   FROM (((profiles p
     LEFT JOIN companies c ON ((p.company_id = c.id)))
     LEFT JOIN politicians pol ON ((p.politician_id = pol.id)))
     LEFT JOIN profiles_to_topics top ON ((top.profile_id = top.profile_id)))
  GROUP BY p.id, p.name, p.surname, p.user_type, p.countries, p.newsletter_frequency, p.embedding, c.id, pol.id;



