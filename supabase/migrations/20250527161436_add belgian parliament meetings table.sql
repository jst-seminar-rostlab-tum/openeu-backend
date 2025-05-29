create table "public"."belgian_parliament_meetings" (
    "id" text not null,
    "title" text not null,
    "title_en" text not null,
    "description" text,
    "description_en" text,
    "meeting_date" date not null,
    "location" text not null,
    "meeting_url" text not null,
    "embedding_input" text not null,
    "scraped_at" timestamp with time zone not null default now()
);


CREATE UNIQUE INDEX belgian_parliament_meetings_pkey ON public.belgian_parliament_meetings USING btree (id);

alter table "public"."belgian_parliament_meetings" add constraint "belgian_parliament_meetings_pkey" PRIMARY KEY using index "belgian_parliament_meetings_pkey";

grant delete on table "public"."belgian_parliament_meetings" to "anon";

grant insert on table "public"."belgian_parliament_meetings" to "anon";

grant references on table "public"."belgian_parliament_meetings" to "anon";

grant select on table "public"."belgian_parliament_meetings" to "anon";

grant trigger on table "public"."belgian_parliament_meetings" to "anon";

grant truncate on table "public"."belgian_parliament_meetings" to "anon";

grant update on table "public"."belgian_parliament_meetings" to "anon";

grant delete on table "public"."belgian_parliament_meetings" to "authenticated";

grant insert on table "public"."belgian_parliament_meetings" to "authenticated";

grant references on table "public"."belgian_parliament_meetings" to "authenticated";

grant select on table "public"."belgian_parliament_meetings" to "authenticated";

grant trigger on table "public"."belgian_parliament_meetings" to "authenticated";

grant truncate on table "public"."belgian_parliament_meetings" to "authenticated";

grant update on table "public"."belgian_parliament_meetings" to "authenticated";

grant delete on table "public"."belgian_parliament_meetings" to "service_role";

grant insert on table "public"."belgian_parliament_meetings" to "service_role";

grant references on table "public"."belgian_parliament_meetings" to "service_role";

grant select on table "public"."belgian_parliament_meetings" to "service_role";

grant trigger on table "public"."belgian_parliament_meetings" to "service_role";

grant truncate on table "public"."belgian_parliament_meetings" to "service_role";

grant update on table "public"."belgian_parliament_meetings" to "service_role";


