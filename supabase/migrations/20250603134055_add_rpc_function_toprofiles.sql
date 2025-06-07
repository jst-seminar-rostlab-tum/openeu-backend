set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.get_user_by_id(uid uuid)
 RETURNS TABLE(email text)
 LANGUAGE plpgsql
 SECURITY DEFINER
AS $function$
begin
  return query
  select email from auth.users where id = uid;
end;
$function$
;


