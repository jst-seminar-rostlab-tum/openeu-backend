create table "public"."ec_res_inno_meetings" (
    "id" text not null default (gen_random_uuid())::text,
    "title" text not null,
    "meeting_url" text not null,
    "start_date" date not null,
    "end_date" date,
    "location" text not null,
    "event_type" text not null,
    "description" text not null,
    "subjects" text[] default '{}'::text[],
    "embedding_input" text,
    "scraped_at" timestamp with time zone not null default now()
);


CREATE UNIQUE INDEX ec_res_inno_meetings_pkey ON public.ec_res_inno_meetings USING btree (id);

alter table "public"."ec_res_inno_meetings" add constraint "ec_res_inno_meetings_pkey" PRIMARY KEY using index "ec_res_inno_meetings_pkey";

grant delete on table "public"."ec_res_inno_meetings" to "anon";

grant insert on table "public"."ec_res_inno_meetings" to "anon";

grant references on table "public"."ec_res_inno_meetings" to "anon";

grant select on table "public"."ec_res_inno_meetings" to "anon";

grant trigger on table "public"."ec_res_inno_meetings" to "anon";

grant truncate on table "public"."ec_res_inno_meetings" to "anon";

grant update on table "public"."ec_res_inno_meetings" to "anon";

grant delete on table "public"."ec_res_inno_meetings" to "authenticated";

grant insert on table "public"."ec_res_inno_meetings" to "authenticated";

grant references on table "public"."ec_res_inno_meetings" to "authenticated";

grant select on table "public"."ec_res_inno_meetings" to "authenticated";

grant trigger on table "public"."ec_res_inno_meetings" to "authenticated";

grant truncate on table "public"."ec_res_inno_meetings" to "authenticated";

grant update on table "public"."ec_res_inno_meetings" to "authenticated";

grant delete on table "public"."ec_res_inno_meetings" to "service_role";

grant insert on table "public"."ec_res_inno_meetings" to "service_role";

grant references on table "public"."ec_res_inno_meetings" to "service_role";

grant select on table "public"."ec_res_inno_meetings" to "service_role";

grant trigger on table "public"."ec_res_inno_meetings" to "service_role";

grant truncate on table "public"."ec_res_inno_meetings" to "service_role";

grant update on table "public"."ec_res_inno_meetings" to "service_role";


