create table if not exists public.country_map_meetings (
    source_table text primary key,
    country      text not null,
    iso2         char(2) not null
);

insert into public.country_map_meetings (source_table, country, iso2) values
  ('mep_meetings',                   'European Union', 'EU'),
  ('ep_meetings',                    'European Union', 'EU'),
  ('austrian_parliament_meetings',   'Austria',        'AT'),
  ('ipex_events',                    'European Union', 'EU'),
  ('belgian_parliament_meetings',    'Belgium',        'BE'),
  ('mec_prep_bodies_meeting',        'European Union', 'EU'),
  ('mec_summit_ministerial_meeting', 'European Union', 'EU'),
  ('polish_presidency_meeting',      'Poland',         'PL'),
  ('spanish_commission_meetings',    'Spain',          'ES'),
  ('weekly_agenda',                  'European Union', 'EU'),
  ('ec_res_inno_meetings',           'European Union', 'EU'),
  ('nl_twka_meetings',               'Netherlands',    'NL')
on conflict (source_table) do update
  set country = excluded.country,
      iso2    = excluded.iso2;

