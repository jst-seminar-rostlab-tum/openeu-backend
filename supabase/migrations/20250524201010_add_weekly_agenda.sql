create sequence "public"."weekly_agenda_id_seq";

create table "public"."weekly_agenda" (
    "id" integer not null default nextval('weekly_agenda_id_seq'::regclass),
    "type" text not null,
    "date" date not null,
    "time" text,
    "title" text not null,
    "committee" text,
    "location" text,
    "description" text
);


alter sequence "public"."weekly_agenda_id_seq" owned by "public"."weekly_agenda"."id";

CREATE UNIQUE INDEX weekly_agenda_pkey ON public.weekly_agenda USING btree (id);

alter table "public"."weekly_agenda" add constraint "weekly_agenda_pkey" PRIMARY KEY using index "weekly_agenda_pkey";

grant delete on table "public"."weekly_agenda" to "anon";

grant insert on table "public"."weekly_agenda" to "anon";

grant references on table "public"."weekly_agenda" to "anon";

grant select on table "public"."weekly_agenda" to "anon";

grant trigger on table "public"."weekly_agenda" to "anon";

grant truncate on table "public"."weekly_agenda" to "anon";

grant update on table "public"."weekly_agenda" to "anon";

grant delete on table "public"."weekly_agenda" to "authenticated";

grant insert on table "public"."weekly_agenda" to "authenticated";

grant references on table "public"."weekly_agenda" to "authenticated";

grant select on table "public"."weekly_agenda" to "authenticated";

grant trigger on table "public"."weekly_agenda" to "authenticated";

grant truncate on table "public"."weekly_agenda" to "authenticated";

grant update on table "public"."weekly_agenda" to "authenticated";

grant delete on table "public"."weekly_agenda" to "service_role";

grant insert on table "public"."weekly_agenda" to "service_role";

grant references on table "public"."weekly_agenda" to "service_role";

grant select on table "public"."weekly_agenda" to "service_role";

grant trigger on table "public"."weekly_agenda" to "service_role";

grant truncate on table "public"."weekly_agenda" to "service_role";

grant update on table "public"."weekly_agenda" to "service_role";


