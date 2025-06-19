set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.get_meeting_tables()
 RETURNS TABLE(source_table text)
 LANGUAGE sql
AS $function$
  SELECT DISTINCT source_table
  FROM public.v_meetings
  ORDER BY source_table;
$function$
;


