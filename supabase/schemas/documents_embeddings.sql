
create table documents_embeddings (
  id            uuid             primary key default gen_random_uuid(),
  source_table  text             not null,
  source_id     text             not null,
  content_type  text             not null,   -- 'protocol', 'calendar', 'document'
  content_text  text             not null,
  embedding     vector(1536)      not null,   
  created_at    timestamptz      default now()
  CONSTRAINT no_duplicates UNIQUE (source_table, source_id, content_text)

);
create index on documents_embeddings using ivfflat(embedding vector_l2_ops) with (lists = 100);

--TODO: Analyze should be run on the table every 10000 updates or so to keep ivfflat efficient!