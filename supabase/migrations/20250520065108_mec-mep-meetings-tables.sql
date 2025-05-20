create sequence "public"."mec_summit_ministerial_meeting_id_seq";

create table "public"."mec_summit_ministerial_meeting" (
    "id" integer not null default nextval('mec_summit_ministerial_meeting_id_seq'::regclass),
    "url" text not null,
    "title" text not null,
    "meeting_date" date not null,
    "meeting_end_date" date,
    "category_abbr" text
);


create table "public"."mep_meeting_attendee_mapping" (
    "meeting_id" uuid not null,
    "attendee_id" uuid not null
);


create table "public"."mep_meeting_attendees" (
    "id" uuid not null default gen_random_uuid(),
    "name" text not null,
    "transparency_register_url" text
);


create table "public"."mep_meetings" (
    "id" uuid not null default gen_random_uuid(),
    "title" text not null,
    "member_name" text not null,
    "meeting_date" date not null,
    "meeting_location" text not null,
    "member_capacity" text not null,
    "procedure_reference" text,
    "associated_committee_or_delegation_code" text,
    "associated_committee_or_delegation_name" text
);


alter sequence "public"."mec_summit_ministerial_meeting_id_seq" owned by "public"."mec_summit_ministerial_meeting"."id";

CREATE UNIQUE INDEX mec_summit_ministerial_meeting_pkey ON public.mec_summit_ministerial_meeting USING btree (id);

CREATE UNIQUE INDEX mec_summit_ministerial_meeting_url_key ON public.mec_summit_ministerial_meeting USING btree (url);

CREATE UNIQUE INDEX mep_meeting_attendee_mapping_pkey ON public.mep_meeting_attendee_mapping USING btree (meeting_id, attendee_id);

CREATE UNIQUE INDEX mep_meeting_attendees_pkey ON public.mep_meeting_attendees USING btree (id);

CREATE UNIQUE INDEX mep_meeting_attendees_transparency_register_url_key ON public.mep_meeting_attendees USING btree (transparency_register_url);

CREATE UNIQUE INDEX mep_meetings_pkey ON public.mep_meetings USING btree (id);

alter table "public"."mec_summit_ministerial_meeting" add constraint "mec_summit_ministerial_meeting_pkey" PRIMARY KEY using index "mec_summit_ministerial_meeting_pkey";

alter table "public"."mep_meeting_attendee_mapping" add constraint "mep_meeting_attendee_mapping_pkey" PRIMARY KEY using index "mep_meeting_attendee_mapping_pkey";

alter table "public"."mep_meeting_attendees" add constraint "mep_meeting_attendees_pkey" PRIMARY KEY using index "mep_meeting_attendees_pkey";

alter table "public"."mep_meetings" add constraint "mep_meetings_pkey" PRIMARY KEY using index "mep_meetings_pkey";

alter table "public"."mec_summit_ministerial_meeting" add constraint "mec_summit_ministerial_meeting_url_key" UNIQUE using index "mec_summit_ministerial_meeting_url_key";

alter table "public"."mep_meeting_attendee_mapping" add constraint "mep_meeting_attendee_mapping_attendee_id_fkey" FOREIGN KEY (attendee_id) REFERENCES mep_meeting_attendees(id) ON DELETE CASCADE not valid;

alter table "public"."mep_meeting_attendee_mapping" validate constraint "mep_meeting_attendee_mapping_attendee_id_fkey";

alter table "public"."mep_meeting_attendee_mapping" add constraint "mep_meeting_attendee_mapping_meeting_id_fkey" FOREIGN KEY (meeting_id) REFERENCES mep_meetings(id) ON DELETE CASCADE not valid;

alter table "public"."mep_meeting_attendee_mapping" validate constraint "mep_meeting_attendee_mapping_meeting_id_fkey";

alter table "public"."mep_meeting_attendees" add constraint "mep_meeting_attendees_transparency_register_url_key" UNIQUE using index "mep_meeting_attendees_transparency_register_url_key";

grant delete on table "public"."mec_summit_ministerial_meeting" to "anon";

grant insert on table "public"."mec_summit_ministerial_meeting" to "anon";

grant references on table "public"."mec_summit_ministerial_meeting" to "anon";

grant select on table "public"."mec_summit_ministerial_meeting" to "anon";

grant trigger on table "public"."mec_summit_ministerial_meeting" to "anon";

grant truncate on table "public"."mec_summit_ministerial_meeting" to "anon";

grant update on table "public"."mec_summit_ministerial_meeting" to "anon";

grant delete on table "public"."mec_summit_ministerial_meeting" to "authenticated";

grant insert on table "public"."mec_summit_ministerial_meeting" to "authenticated";

grant references on table "public"."mec_summit_ministerial_meeting" to "authenticated";

grant select on table "public"."mec_summit_ministerial_meeting" to "authenticated";

grant trigger on table "public"."mec_summit_ministerial_meeting" to "authenticated";

grant truncate on table "public"."mec_summit_ministerial_meeting" to "authenticated";

grant update on table "public"."mec_summit_ministerial_meeting" to "authenticated";

grant delete on table "public"."mec_summit_ministerial_meeting" to "service_role";

grant insert on table "public"."mec_summit_ministerial_meeting" to "service_role";

grant references on table "public"."mec_summit_ministerial_meeting" to "service_role";

grant select on table "public"."mec_summit_ministerial_meeting" to "service_role";

grant trigger on table "public"."mec_summit_ministerial_meeting" to "service_role";

grant truncate on table "public"."mec_summit_ministerial_meeting" to "service_role";

grant update on table "public"."mec_summit_ministerial_meeting" to "service_role";

grant delete on table "public"."mep_meeting_attendee_mapping" to "anon";

grant insert on table "public"."mep_meeting_attendee_mapping" to "anon";

grant references on table "public"."mep_meeting_attendee_mapping" to "anon";

grant select on table "public"."mep_meeting_attendee_mapping" to "anon";

grant trigger on table "public"."mep_meeting_attendee_mapping" to "anon";

grant truncate on table "public"."mep_meeting_attendee_mapping" to "anon";

grant update on table "public"."mep_meeting_attendee_mapping" to "anon";

grant delete on table "public"."mep_meeting_attendee_mapping" to "authenticated";

grant insert on table "public"."mep_meeting_attendee_mapping" to "authenticated";

grant references on table "public"."mep_meeting_attendee_mapping" to "authenticated";

grant select on table "public"."mep_meeting_attendee_mapping" to "authenticated";

grant trigger on table "public"."mep_meeting_attendee_mapping" to "authenticated";

grant truncate on table "public"."mep_meeting_attendee_mapping" to "authenticated";

grant update on table "public"."mep_meeting_attendee_mapping" to "authenticated";

grant delete on table "public"."mep_meeting_attendee_mapping" to "service_role";

grant insert on table "public"."mep_meeting_attendee_mapping" to "service_role";

grant references on table "public"."mep_meeting_attendee_mapping" to "service_role";

grant select on table "public"."mep_meeting_attendee_mapping" to "service_role";

grant trigger on table "public"."mep_meeting_attendee_mapping" to "service_role";

grant truncate on table "public"."mep_meeting_attendee_mapping" to "service_role";

grant update on table "public"."mep_meeting_attendee_mapping" to "service_role";

grant delete on table "public"."mep_meeting_attendees" to "anon";

grant insert on table "public"."mep_meeting_attendees" to "anon";

grant references on table "public"."mep_meeting_attendees" to "anon";

grant select on table "public"."mep_meeting_attendees" to "anon";

grant trigger on table "public"."mep_meeting_attendees" to "anon";

grant truncate on table "public"."mep_meeting_attendees" to "anon";

grant update on table "public"."mep_meeting_attendees" to "anon";

grant delete on table "public"."mep_meeting_attendees" to "authenticated";

grant insert on table "public"."mep_meeting_attendees" to "authenticated";

grant references on table "public"."mep_meeting_attendees" to "authenticated";

grant select on table "public"."mep_meeting_attendees" to "authenticated";

grant trigger on table "public"."mep_meeting_attendees" to "authenticated";

grant truncate on table "public"."mep_meeting_attendees" to "authenticated";

grant update on table "public"."mep_meeting_attendees" to "authenticated";

grant delete on table "public"."mep_meeting_attendees" to "service_role";

grant insert on table "public"."mep_meeting_attendees" to "service_role";

grant references on table "public"."mep_meeting_attendees" to "service_role";

grant select on table "public"."mep_meeting_attendees" to "service_role";

grant trigger on table "public"."mep_meeting_attendees" to "service_role";

grant truncate on table "public"."mep_meeting_attendees" to "service_role";

grant update on table "public"."mep_meeting_attendees" to "service_role";

grant delete on table "public"."mep_meetings" to "anon";

grant insert on table "public"."mep_meetings" to "anon";

grant references on table "public"."mep_meetings" to "anon";

grant select on table "public"."mep_meetings" to "anon";

grant trigger on table "public"."mep_meetings" to "anon";

grant truncate on table "public"."mep_meetings" to "anon";

grant update on table "public"."mep_meetings" to "anon";

grant delete on table "public"."mep_meetings" to "authenticated";

grant insert on table "public"."mep_meetings" to "authenticated";

grant references on table "public"."mep_meetings" to "authenticated";

grant select on table "public"."mep_meetings" to "authenticated";

grant trigger on table "public"."mep_meetings" to "authenticated";

grant truncate on table "public"."mep_meetings" to "authenticated";

grant update on table "public"."mep_meetings" to "authenticated";

grant delete on table "public"."mep_meetings" to "service_role";

grant insert on table "public"."mep_meetings" to "service_role";

grant references on table "public"."mep_meetings" to "service_role";

grant select on table "public"."mep_meetings" to "service_role";

grant trigger on table "public"."mep_meetings" to "service_role";

grant truncate on table "public"."mep_meetings" to "service_role";

grant update on table "public"."mep_meetings" to "service_role";


