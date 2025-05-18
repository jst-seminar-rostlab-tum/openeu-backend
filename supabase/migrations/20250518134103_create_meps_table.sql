create table "public"."meps" (
    "id" text not null,
    "type" text not null,
    "label" text not null,
    "family_name" text not null,
    "given_name" text not null,
    "sort_label" text not null,
    "country_of_representation" text not null,
    "political_group" text not null,
    "official_family_name" text,
    "official_given_name" text
);


CREATE UNIQUE INDEX meps_pkey ON public.meps USING btree (id);

alter table "public"."meps" add constraint "meps_pkey" PRIMARY KEY using index "meps_pkey";

grant delete on table "public"."meps" to "anon";

grant insert on table "public"."meps" to "anon";

grant references on table "public"."meps" to "anon";

grant select on table "public"."meps" to "anon";

grant trigger on table "public"."meps" to "anon";

grant truncate on table "public"."meps" to "anon";

grant update on table "public"."meps" to "anon";

grant delete on table "public"."meps" to "authenticated";

grant insert on table "public"."meps" to "authenticated";

grant references on table "public"."meps" to "authenticated";

grant select on table "public"."meps" to "authenticated";

grant trigger on table "public"."meps" to "authenticated";

grant truncate on table "public"."meps" to "authenticated";

grant update on table "public"."meps" to "authenticated";

grant delete on table "public"."meps" to "service_role";

grant insert on table "public"."meps" to "service_role";

grant references on table "public"."meps" to "service_role";

grant select on table "public"."meps" to "service_role";

grant trigger on table "public"."meps" to "service_role";

grant truncate on table "public"."meps" to "service_role";

grant update on table "public"."meps" to "service_role";


