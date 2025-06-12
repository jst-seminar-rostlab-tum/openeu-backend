CREATE OR REPLACE FUNCTION public.get_meetings_by_filter(
    source_tables text[],
    source_ids text[],
    max_results integer,
    start_date timestamp with time zone DEFAULT NULL,
    end_date timestamp with time zone DEFAULT NULL,
    country text DEFAULT NULL
)
RETURNS SETOF v_meetings
LANGUAGE sql
AS $$
    SELECT vm.*
    FROM v_meetings vm
    JOIN unnest(source_tables, source_ids) AS src(source_table, source_id)
      ON vm.source_table = src.source_table
     AND vm.source_id = src.source_id
    WHERE (start_date IS NULL OR vm.meeting_start_datetime >= start_date)
      AND (end_date IS NULL OR vm.meeting_start_datetime <= end_date)
      AND (country IS NULL OR LOWER(vm.location) = LOWER(country))
    LIMIT max_results;
$$;