set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.get_countries()
 RETURNS text[]
 LANGUAGE sql
AS $function$
  SELECT array_agg(DISTINCT location)
  FROM public.v_meetings;
$function$
;


