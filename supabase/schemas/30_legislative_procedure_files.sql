-- Legislative Procedure Files
CREATE TABLE IF NOT EXISTS legislative_procedure_files (
    id TEXT PRIMARY KEY NOT NULL,
    link TEXT NOT NULL,
    extracted_text TEXT NOT NULL,
    scraped_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    UNIQUE (id)
);