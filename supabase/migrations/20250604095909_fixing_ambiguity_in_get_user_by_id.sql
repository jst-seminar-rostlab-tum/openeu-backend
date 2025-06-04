drop function if exists "public"."get_user_by_id"(uid uuid);

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.get_user_by_id(uid uuid)
 RETURNS text
 LANGUAGE sql
 SECURITY DEFINER
AS $function$
  SELECT email
    FROM auth.users
   WHERE id = $1;
$function$
;


