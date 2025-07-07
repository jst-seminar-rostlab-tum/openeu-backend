CREATE OR REPLACE VIEW public.v_profiles AS
SELECT
    p.id,
    p.name,
    p.surname,
    p.user_type,
    p.countries,
    p.newsletter_frequency,
    p.embedding_input,
    p.embedding,

    -- Company-related fields (for entrepreneurs)
    row_to_json(c) AS company,

    -- Politician-related fields (for politicians)
    row_to_json(pol) AS politician,

    -- Topics related to the profile
    array_remove(array_agg(DISTINCT top.topic_id), NULL) AS topic_ids
FROM profiles p
LEFT JOIN companies c ON p.company_id = c.id
LEFT JOIN politicians pol ON p.politician_id = pol.id
LEFT JOIN profiles_to_topics top ON p.id = top.profile_id
GROUP BY
    p.id,
    p.name,
    p.surname,
    p.user_type,
    p.countries,
    p.newsletter_frequency,
    p.embedding_input,
    p.embedding,
    c.id,
    pol.id;
