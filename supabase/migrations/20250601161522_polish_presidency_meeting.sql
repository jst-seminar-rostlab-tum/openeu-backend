create table "public"."polish_presidency_meeting" (
    "id" text not null default (gen_random_uuid())::text,
    "title" text not null,
    "meeting_date" date not null,
    "meeting_end_date" date,
    "meeting_location" text not null,
    "meeting_url" text not null,
    "embedding_input" text,
    "scraped_at" timestamp with time zone not null default now()
);


CREATE UNIQUE INDEX polish_presidency_meeting_pkey ON public.polish_presidency_meeting USING btree (id);

alter table "public"."polish_presidency_meeting" add constraint "polish_presidency_meeting_pkey" PRIMARY KEY using index "polish_presidency_meeting_pkey";

grant delete on table "public"."polish_presidency_meeting" to "anon";

grant insert on table "public"."polish_presidency_meeting" to "anon";

grant references on table "public"."polish_presidency_meeting" to "anon";

grant select on table "public"."polish_presidency_meeting" to "anon";

grant trigger on table "public"."polish_presidency_meeting" to "anon";

grant truncate on table "public"."polish_presidency_meeting" to "anon";

grant update on table "public"."polish_presidency_meeting" to "anon";

grant delete on table "public"."polish_presidency_meeting" to "authenticated";

grant insert on table "public"."polish_presidency_meeting" to "authenticated";

grant references on table "public"."polish_presidency_meeting" to "authenticated";

grant select on table "public"."polish_presidency_meeting" to "authenticated";

grant trigger on table "public"."polish_presidency_meeting" to "authenticated";

grant truncate on table "public"."polish_presidency_meeting" to "authenticated";

grant update on table "public"."polish_presidency_meeting" to "authenticated";

grant delete on table "public"."polish_presidency_meeting" to "service_role";

grant insert on table "public"."polish_presidency_meeting" to "service_role";

grant references on table "public"."polish_presidency_meeting" to "service_role";

grant select on table "public"."polish_presidency_meeting" to "service_role";

grant trigger on table "public"."polish_presidency_meeting" to "service_role";

grant truncate on table "public"."polish_presidency_meeting" to "service_role";

grant update on table "public"."polish_presidency_meeting" to "service_role";


