CREATE TABLE IF NOT EXISTS bt_documents (
  id                TEXT PRIMARY KEY,
  datum             DATE,
  titel             TEXT,
  drucksachetyp     TEXT,
  text              TEXT,
  title_english     TEXT,
  scraped_at        timestamp with time zone NOT NULL DEFAULT now()
);