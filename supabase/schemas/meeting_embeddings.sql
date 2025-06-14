create extension vector;

create table meeting_embeddings (
  id            text             primary key default gen_random_uuid()::text,
  source_table  text             not null,
  source_id     text             not null,
  content_column  text             not null,
  content_text  text             not null,
  embedding     vector(1536)      not null,   
  created_at    timestamptz      default now(),
  CONSTRAINT no_duplicates UNIQUE (source_table, source_id)
);
create index on documents_embeddings using ivfflat(embedding vector_l2_ops) with (lists = 100);

--TODO: Analyze should be run on the table every 10000 updates or so to keep ivfflat efficient!

--Remote Procedure Call to query for K-NN
-- src_tables:   list of table names
-- content_columns: corresponding list of column names
-- query_embedding: the vector
-- match_count: 5

create or replace function public.match_filtered_meetings(
  src_tables      text[],
  content_columns text[],
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
declare
  max_dist float := sqrt(1536);  -- approx. 39.1918
begin
  return query
    select
      e.source_table,
      e.source_id,
      e.content_text,
      ((1 - (e.embedding <#> query_embedding))/2) as similarity
    from meeting_embeddings e
    where
      e.source_table = any(src_tables)
      and e.content_column = any(content_columns)
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$$;


create or replace function public.match_default_meetings(
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
declare
  max_dist float := sqrt(1536);
begin
  return query
    select
      e.source_table,
      e.source_id,
      e.content_text,
      ((1 - (e.embedding <#> query_embedding))/2) as similarity
    from meeting_embeddings e
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$$;


-- combined K‑NN over both tables
create or replace function public.match_combined_embeddings(
  query_embedding vector(1536),
  match_count     int
)
returns table(
  source_table  text,
  source_id     text,
  content_text  text,
  similarity    float
)
language sql
stable
as $$
  with all_embeddings as (
    select
      source_table,
      source_id,
      content_text,
      embedding
    from meeting_embeddings
    union all
    select
      source_table,
      source_id,
      content_text,
      embedding
    from document_embeddings
  )
  select
    ae.source_table,
    ae.source_id,
    ae.content_text,
    -- convert cosine distance to a [0–1] similarity score
    (1 - (ae.embedding <#> query_embedding)) as similarity
  from all_embeddings ae
  order by ae.embedding <#> query_embedding
  limit match_count;
$$;

CREATE OR REPLACE FUNCTION public.match_combined_filtered_embeddings(
  src_tables      TEXT[],            -- list of source_table values to include
  query_embedding VECTOR(1536),      -- your query vector
  match_count     INT                -- number of neighbors to return
)
RETURNS TABLE (
  source_table  TEXT,
  source_id     TEXT,
  content_text  TEXT,
  similarity    FLOAT
)
LANGUAGE SQL
STABLE
AS $$
  WITH all_embeddings AS (
    SELECT
      source_table,
      source_id,
      content_text,
      embedding
    FROM meeting_embeddings
    UNION ALL
    SELECT
      source_table,
      source_id,
      content_text,
      embedding
    FROM document_embeddings
  )
  SELECT
    ae.source_table,
    ae.source_id,
    ae.content_text,
    (1 - (ae.embedding <#> query_embedding)) AS similarity
  FROM all_embeddings ae
  WHERE ae.source_table = ANY(src_tables)
  ORDER BY ae.embedding <#> query_embedding
  LIMIT match_count;
$$;