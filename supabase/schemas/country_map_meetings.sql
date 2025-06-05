create table if not exists public.country_map_meetings (
    source_table text primary key,
    country      text not null,
    iso2         char(2) not null
);