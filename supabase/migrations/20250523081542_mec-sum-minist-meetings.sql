create sequence "public"."mec_summit_ministerial_meeting_id_seq";

create table "public"."mec_summit_ministerial_meeting" (
    "id" integer not null default nextval('mec_summit_ministerial_meeting_id_seq'::regclass),
    "url" text not null,
    "title" text not null,
    "meeting_date" date not null,
    "meeting_end_date" date,
    "category_abbr" text
);


alter sequence "public"."mec_summit_ministerial_meeting_id_seq" owned by "public"."mec_summit_ministerial_meeting"."id";

CREATE UNIQUE INDEX mec_summit_ministerial_meeting_pkey ON public.mec_summit_ministerial_meeting USING btree (id);

CREATE UNIQUE INDEX mec_summit_ministerial_meeting_url_key ON public.mec_summit_ministerial_meeting USING btree (url);

alter table "public"."mec_summit_ministerial_meeting" add constraint "mec_summit_ministerial_meeting_pkey" PRIMARY KEY using index "mec_summit_ministerial_meeting_pkey";

alter table "public"."mec_summit_ministerial_meeting" add constraint "mec_summit_ministerial_meeting_url_key" UNIQUE using index "mec_summit_ministerial_meeting_url_key";

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


