create table "public"."meeting_topic_assignments" (
    "id" text not null default (gen_random_uuid())::text,
    "source_id" text not null,
    "source_table" text not null,
    "topic_id" text not null
);

CREATE UNIQUE INDEX meeting_topic_assignments_pkey ON public.meeting_topic_assignments USING btree (id);

CREATE UNIQUE INDEX meeting_topics_pkey ON public.meeting_topics USING btree (id);

alter table "public"."meeting_topic_assignments" add constraint "meeting_topic_assignments_pkey" PRIMARY KEY using index "meeting_topic_assignments_pkey";

alter table "public"."meeting_topics" add constraint "meeting_topics_pkey" PRIMARY KEY using index "meeting_topics_pkey";

grant delete on table "public"."meeting_topic_assignments" to "anon";

grant insert on table "public"."meeting_topic_assignments" to "anon";

grant references on table "public"."meeting_topic_assignments" to "anon";

grant select on table "public"."meeting_topic_assignments" to "anon";

grant trigger on table "public"."meeting_topic_assignments" to "anon";

grant truncate on table "public"."meeting_topic_assignments" to "anon";

grant update on table "public"."meeting_topic_assignments" to "anon";

grant delete on table "public"."meeting_topic_assignments" to "authenticated";

grant insert on table "public"."meeting_topic_assignments" to "authenticated";

grant references on table "public"."meeting_topic_assignments" to "authenticated";

grant select on table "public"."meeting_topic_assignments" to "authenticated";

grant trigger on table "public"."meeting_topic_assignments" to "authenticated";

grant truncate on table "public"."meeting_topic_assignments" to "authenticated";

grant update on table "public"."meeting_topic_assignments" to "authenticated";

grant delete on table "public"."meeting_topic_assignments" to "service_role";

grant insert on table "public"."meeting_topic_assignments" to "service_role";

grant references on table "public"."meeting_topic_assignments" to "service_role";

grant select on table "public"."meeting_topic_assignments" to "service_role";

grant trigger on table "public"."meeting_topic_assignments" to "service_role";

grant truncate on table "public"."meeting_topic_assignments" to "service_role";

grant update on table "public"."meeting_topic_assignments" to "service_role";


