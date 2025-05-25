create extension vector;

create table documents_embeddings (
  id            uuid             primary key default gen_random_uuid(),
  source_table  text             not null,
  source_id     text             not null,
  content_column  text             not null,   -- 'protocol', 'calendar', 'document'
  content_text  text             not null,
  embedding     vector(1536)      not null,   
  created_at    timestamptz      default now(),
  CONSTRAINT no_duplicates UNIQUE (source_table, source_id, content_text)
);
create index on documents_embeddings using ivfflat(embedding vector_l2_ops) with (lists = 100);

--TODO: Analyze should be run on the table every 10000 updates or so to keep ivfflat efficient!




--Remote Procedure Call to query for K-NN
-- src_tables:   list of table names
-- content_columns: corresponding list of column names
-- query_embedding: the vector
-- match_count: 5

create or replace function public.match_filtered(
  src_tables      text[],
  content_columns   text[],
  query_embedding vector,
  match_count     int
)
returns table(
  source_table  text,
  source_id     text,
  content_text  text,
  similarity    float
)
language plpgsql
as $$
begin
  return query
    select
      e.source_table,
      e.source_id,
      e.content_text,
      1 - (e.embedding <#> query_embedding) as similarity
    from documents_embeddings e
    where
      e.source_table = any(src_tables)
      and e.content_column = any(content_columns)
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$$;


create or replace function public.match_default(
  query_embedding vector,
  match_count     int
)
returns table(
  source_table  text,
  source_id     text,
  content_text  text,
  similarity    float
)
language plpgsql
as $$
begin
  return query
    select
      e.source_table,
      e.source_id,
      e.content_text,
      1 - (e.embedding <#> query_embedding) as similarity
    from documents_embeddings e
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$$;