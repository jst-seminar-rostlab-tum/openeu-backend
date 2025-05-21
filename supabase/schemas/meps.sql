CREATE TABLE meps (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  label TEXT NOT NULL,
  family_name TEXT NOT NULL,
  given_name TEXT NOT NULL,
  sort_label TEXT NOT NULL,
  country_of_representation TEXT NOT NULL,
  political_group TEXT NOT NULL,
  official_family_name TEXT,
  official_given_name TEXT
);