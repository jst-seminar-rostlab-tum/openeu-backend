create table "public"."mec_prep_bodies_meeting" (
    "id" integer not null,
    "url" text not null,
    "title" text not null,
    "meeting_timestamp" timestamp without time zone not null,
    "meeting_location" text not null,
    "embedding_input" text not null
);
CREATE UNIQUE INDEX mec_prep_bodies_meeting_pkey ON public.mec_prep_bodies_meeting USING btree (id);
alter table "public"."mec_prep_bodies_meeting" add constraint "mec_prep_bodies_meeting_pkey" PRIMARY KEY using index "mec_prep_bodies_meeting_pkey";
grant delete on table "public"."mec_prep_bodies_meeting" to "anon";
grant insert on table "public"."mec_prep_bodies_meeting" to "anon";
grant references on table "public"."mec_prep_bodies_meeting" to "anon";
grant select on table "public"."mec_prep_bodies_meeting" to "anon";
grant trigger on table "public"."mec_prep_bodies_meeting" to "anon";
grant truncate on table "public"."mec_prep_bodies_meeting" to "anon";
grant update on table "public"."mec_prep_bodies_meeting" to "anon";
grant delete on table "public"."mec_prep_bodies_meeting" to "authenticated";
grant insert on table "public"."mec_prep_bodies_meeting" to "authenticated";
grant references on table "public"."mec_prep_bodies_meeting" to "authenticated";
grant select on table "public"."mec_prep_bodies_meeting" to "authenticated";
grant trigger on table "public"."mec_prep_bodies_meeting" to "authenticated";
grant truncate on table "public"."mec_prep_bodies_meeting" to "authenticated";
grant update on table "public"."mec_prep_bodies_meeting" to "authenticated";
grant delete on table "public"."mec_prep_bodies_meeting" to "service_role";
grant insert on table "public"."mec_prep_bodies_meeting" to "service_role";
grant references on table "public"."mec_prep_bodies_meeting" to "service_role";
grant select on table "public"."mec_prep_bodies_meeting" to "service_role";
grant trigger on table "public"."mec_prep_bodies_meeting" to "service_role";
grant truncate on table "public"."mec_prep_bodies_meeting" to "service_role";
grant update on table "public"."mec_prep_bodies_meeting" to "service_role";
