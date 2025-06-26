create table meeting_embeddings (
  id            text             primary key default gen_random_uuid()::text,
  source_table  text             not null,
  source_id     text             not null,
  content_column  text             not null,
  content_text  text             not null,
  embedding     vector(1536)      not null,   
  created_at    timestamptz      default now(),
  CONSTRAINT no_duplicates_meeting UNIQUE (source_table, source_id)
);
create index on meeting_embeddings using ivfflat(embedding vector_l2_ops) with (lists = 100);

--TODO: Analyze should be run on the table every 10000 updates or so to keep ivfflat efficient!

--Remote Procedure Call to query for K-NN
-- src_tables:   list of table names
-- content_columns: corresponding list of column names
-- query_embedding: the vector
-- match_count: 5

create or replace function public.match_filtered_meetings(
  query_embedding    vector,
  match_count        int,
  src_tables         text[]   DEFAULT NULL,
  content_columns    text[]   DEFAULT NULL,
  allowed_topics  text[]   DEFAULT NULL,
  allowed_topic_ids  text[]   DEFAULT NULL,
  allowed_countries  text[]   DEFAULT NULL
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
      ((1 - (e.embedding <#> query_embedding)) / 2) as similarity
    from meeting_embeddings e
    
    where
      -- optional table filter
      (src_tables is null
       or e.source_table = any(src_tables)
      )
      -- optional column filter
      and (content_columns is null
           or e.content_column = any(content_columns)
          )
          
      -- optional topic filter using EXISTS
      and (
        allowed_topic_ids is null
        or exists (
          select 1 from meeting_topic_assignments mta
           where mta.source_table = e.source_table
             and mta.source_id    = e.source_id
             and mta.topic_id = any(allowed_topic_ids)
        )
      )

      and (
        allowed_topics is null
        or exists (
          select 1 from meeting_topic_assignments mta, meeting_topics mt
           where mta.source_table = e.source_table
             and mta.source_id    = e.source_id
             and mta.topic_id = mt.id
             and mt.topic = any(allowed_topics)
        )
      )

      -- optional country filter using EXISTS (only for profiles)
      
    AND (
      allowed_countries IS NULL
      OR LOWER((
        SELECT vm.location
        FROM public.v_meetings vm
        WHERE vm.source_table = e.source_table
          AND vm.source_id = e.source_id)) = ANY (
        SELECT LOWER(country) FROM unnest(allowed_countries) AS country
      )
    )
    order by e.embedding <#> query_embedding
    limit match_count;
end;
$$;


CREATE OR REPLACE FUNCTION public.match_combined_filtered_embeddings(
  query_embedding VECTOR(1536),      -- your query vector
  match_count     INT,                -- number of neighbors to return
  src_tables      TEXT[] DEFAULT NULL,
  content_columns TEXT[] DEFAULT NULL
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
      content_column,
      embedding
    FROM meeting_embeddings
    UNION ALL
    SELECT
      source_table,
      source_id,
      content_text,
      content_column,
      embedding
    FROM documents_embeddings
  )
  SELECT
    ae.source_table,
    ae.source_id,
    ae.content_text,
    ((1 - (ae.embedding <#> query_embedding))/2) AS similarity
  FROM all_embeddings ae
  WHERE (src_tables IS NULL or ae.source_table = ANY(src_tables)) and (content_columns IS NULL or ae.content_column = ANY(content_columns))
  ORDER BY ae.embedding <#> query_embedding
  LIMIT match_count;
$$;

