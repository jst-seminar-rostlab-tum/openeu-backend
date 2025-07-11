create table "public"."subscriptions" (
    "id" uuid not null default gen_random_uuid(),
    "user_id" uuid not null,
    "legislation_id" text not null,
    "created_at" timestamp with time zone default now()
);


CREATE UNIQUE INDEX subscriptions_pkey ON public.subscriptions USING btree (id);

alter table "public"."subscriptions" add constraint "subscriptions_pkey" PRIMARY KEY using index "subscriptions_pkey";

alter table "public"."subscriptions" add constraint "subscriptions_legislation_id_fkey" FOREIGN KEY (legislation_id) REFERENCES legislative_files(id) not valid;

alter table "public"."subscriptions" validate constraint "subscriptions_legislation_id_fkey";

set check_function_bodies = off;

CREATE OR REPLACE FUNCTION public.search_legislation_suggestions(search_text text)
 RETURNS TABLE(id text, title text, similarity_score double precision)
 LANGUAGE sql
AS $function$
  select 
    id,
    title,
    similarity_score
  from (
    select 
      id,
      title,
      GREATEST(
        similarity(title, search_text),
        similarity(id, search_text)
      ) as similarity_score
    from legislative_files
    where (title is not null or id is not null)
  ) scored
  where similarity_score > 0.1
  order by similarity_score desc
  limit 5
$function$
;

grant delete on table "public"."subscriptions" to "anon";

grant insert on table "public"."subscriptions" to "anon";

grant references on table "public"."subscriptions" to "anon";

grant select on table "public"."subscriptions" to "anon";

grant trigger on table "public"."subscriptions" to "anon";

grant truncate on table "public"."subscriptions" to "anon";

grant update on table "public"."subscriptions" to "anon";

grant delete on table "public"."subscriptions" to "authenticated";

grant insert on table "public"."subscriptions" to "authenticated";

grant references on table "public"."subscriptions" to "authenticated";

grant select on table "public"."subscriptions" to "authenticated";

grant trigger on table "public"."subscriptions" to "authenticated";

grant truncate on table "public"."subscriptions" to "authenticated";

grant update on table "public"."subscriptions" to "authenticated";

grant delete on table "public"."subscriptions" to "service_role";

grant insert on table "public"."subscriptions" to "service_role";

grant references on table "public"."subscriptions" to "service_role";

grant select on table "public"."subscriptions" to "service_role";

grant trigger on table "public"."subscriptions" to "service_role";

grant truncate on table "public"."subscriptions" to "service_role";

grant update on table "public"."subscriptions" to "service_role";


