create sequence "public"."ep_meetings_id_seq";

create sequence "public"."meetings_id_seq";

create sequence "public"."people_id_seq";

create table "public"."ep_meetings" (
    "id" integer not null default nextval('ep_meetings_id_seq'::regclass),
    "title" text not null,
    "datetime" timestamp without time zone not null,
    "place" text,
    "subtitles" text
);


create table "public"."meetings" (
    "id" integer not null default nextval('meetings_id_seq'::regclass),
    "name" character varying(255) not null
);


create table "public"."people" (
    "id" integer not null default nextval('people_id_seq'::regclass),
    "name" character varying(255) not null
);


alter sequence "public"."ep_meetings_id_seq" owned by "public"."ep_meetings"."id";

alter sequence "public"."meetings_id_seq" owned by "public"."meetings"."id";

alter sequence "public"."people_id_seq" owned by "public"."people"."id";

CREATE UNIQUE INDEX ep_meetings_pkey ON public.ep_meetings USING btree (id);

CREATE UNIQUE INDEX meetings_pkey ON public.meetings USING btree (id);

CREATE UNIQUE INDEX people_pkey ON public.people USING btree (id);

alter table "public"."ep_meetings" add constraint "ep_meetings_pkey" PRIMARY KEY using index "ep_meetings_pkey";

alter table "public"."meetings" add constraint "meetings_pkey" PRIMARY KEY using index "meetings_pkey";

alter table "public"."people" add constraint "people_pkey" PRIMARY KEY using index "people_pkey";

grant delete on table "public"."ep_meetings" to "anon";

grant insert on table "public"."ep_meetings" to "anon";

grant references on table "public"."ep_meetings" to "anon";

grant select on table "public"."ep_meetings" to "anon";

grant trigger on table "public"."ep_meetings" to "anon";

grant truncate on table "public"."ep_meetings" to "anon";

grant update on table "public"."ep_meetings" to "anon";

grant delete on table "public"."ep_meetings" to "authenticated";

grant insert on table "public"."ep_meetings" to "authenticated";

grant references on table "public"."ep_meetings" to "authenticated";

grant select on table "public"."ep_meetings" to "authenticated";

grant trigger on table "public"."ep_meetings" to "authenticated";

grant truncate on table "public"."ep_meetings" to "authenticated";

grant update on table "public"."ep_meetings" to "authenticated";

grant delete on table "public"."ep_meetings" to "service_role";

grant insert on table "public"."ep_meetings" to "service_role";

grant references on table "public"."ep_meetings" to "service_role";

grant select on table "public"."ep_meetings" to "service_role";

grant trigger on table "public"."ep_meetings" to "service_role";

grant truncate on table "public"."ep_meetings" to "service_role";

grant update on table "public"."ep_meetings" to "service_role";

grant delete on table "public"."meetings" to "anon";

grant insert on table "public"."meetings" to "anon";

grant references on table "public"."meetings" to "anon";

grant select on table "public"."meetings" to "anon";

grant trigger on table "public"."meetings" to "anon";

grant truncate on table "public"."meetings" to "anon";

grant update on table "public"."meetings" to "anon";

grant delete on table "public"."meetings" to "authenticated";

grant insert on table "public"."meetings" to "authenticated";

grant references on table "public"."meetings" to "authenticated";

grant select on table "public"."meetings" to "authenticated";

grant trigger on table "public"."meetings" to "authenticated";

grant truncate on table "public"."meetings" to "authenticated";

grant update on table "public"."meetings" to "authenticated";

grant delete on table "public"."meetings" to "service_role";

grant insert on table "public"."meetings" to "service_role";

grant references on table "public"."meetings" to "service_role";

grant select on table "public"."meetings" to "service_role";

grant trigger on table "public"."meetings" to "service_role";

grant truncate on table "public"."meetings" to "service_role";

grant update on table "public"."meetings" to "service_role";

grant delete on table "public"."people" to "anon";

grant insert on table "public"."people" to "anon";

grant references on table "public"."people" to "anon";

grant select on table "public"."people" to "anon";

grant trigger on table "public"."people" to "anon";

grant truncate on table "public"."people" to "anon";

grant update on table "public"."people" to "anon";

grant delete on table "public"."people" to "authenticated";

grant insert on table "public"."people" to "authenticated";

grant references on table "public"."people" to "authenticated";

grant select on table "public"."people" to "authenticated";

grant trigger on table "public"."people" to "authenticated";

grant truncate on table "public"."people" to "authenticated";

grant update on table "public"."people" to "authenticated";

grant delete on table "public"."people" to "service_role";

grant insert on table "public"."people" to "service_role";

grant references on table "public"."people" to "service_role";

grant select on table "public"."people" to "service_role";

grant trigger on table "public"."people" to "service_role";

grant truncate on table "public"."people" to "service_role";

grant update on table "public"."people" to "service_role";


