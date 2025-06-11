CREATE OR REPLACE FUNCTION public.get_meetings_by_source_arrays(
    source_tables text[],
    source_ids text[],
    max_results integer
)
RETURNS SETOF v_meetings
LANGUAGE sql
AS $$
    SELECT vm.*
    FROM v_meetings vm
    JOIN unnest(source_tables, source_ids) AS src(source_table, source_id)
      ON vm.source_table = src.source_table
     AND vm.source_id = src.source_id
    LIMIT max_results;
$$;