set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.get_meetings_without_embeddings()
 RETURNS SETOF v_meetings
 LANGUAGE sql
AS $function$
    SELECT vm.*
    FROM v_meetings vm
    LEFT JOIN meeting_embeddings me
      ON vm.source_table = me.source_table
     AND vm.source_id = me.source_id
    WHERE me.source_id IS NULL;
$function$
;


