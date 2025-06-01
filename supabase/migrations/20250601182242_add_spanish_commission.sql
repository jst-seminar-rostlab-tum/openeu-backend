create table "public"."spanish_commission_meetings" (
    "id" text not null default (gen_random_uuid())::text,
    "date" date not null,
    "time" text,
    "title" text not null,
    "title_en" text,
    "location" text,
    "location_en" text,
    "description" text,
    "description_en" text,
    "url" text,
    "embedding_input" text,
    "links" jsonb,
    "scraped_at" timestamp with time zone not null default now()
);


CREATE UNIQUE INDEX spanish_commission_meetings_pkey ON public.spanish_commission_meetings USING btree (id);

alter table "public"."spanish_commission_meetings" add constraint "spanish_commission_meetings_pkey" PRIMARY KEY using index "spanish_commission_meetings_pkey";

grant delete on table "public"."spanish_commission_meetings" to "anon";

grant insert on table "public"."spanish_commission_meetings" to "anon";

grant references on table "public"."spanish_commission_meetings" to "anon";

grant select on table "public"."spanish_commission_meetings" to "anon";

grant trigger on table "public"."spanish_commission_meetings" to "anon";

grant truncate on table "public"."spanish_commission_meetings" to "anon";

grant update on table "public"."spanish_commission_meetings" to "anon";

grant delete on table "public"."spanish_commission_meetings" to "authenticated";

grant insert on table "public"."spanish_commission_meetings" to "authenticated";

grant references on table "public"."spanish_commission_meetings" to "authenticated";

grant select on table "public"."spanish_commission_meetings" to "authenticated";

grant trigger on table "public"."spanish_commission_meetings" to "authenticated";

grant truncate on table "public"."spanish_commission_meetings" to "authenticated";

grant update on table "public"."spanish_commission_meetings" to "authenticated";

grant delete on table "public"."spanish_commission_meetings" to "service_role";

grant insert on table "public"."spanish_commission_meetings" to "service_role";

grant references on table "public"."spanish_commission_meetings" to "service_role";

grant select on table "public"."spanish_commission_meetings" to "service_role";

grant trigger on table "public"."spanish_commission_meetings" to "service_role";

grant truncate on table "public"."spanish_commission_meetings" to "service_role";

grant update on table "public"."spanish_commission_meetings" to "service_role";


