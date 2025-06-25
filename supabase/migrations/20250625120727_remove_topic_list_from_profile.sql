alter table "public"."profiles" drop column "topic_list";

alter table "public"."profiles_to_topics" alter column "profile_id" set not null;

alter table "public"."profiles_to_topics" alter column "topic_id" set not null;

CREATE UNIQUE INDEX profiles_to_topics_pkey ON public.profiles_to_topics USING btree (profile_id, topic_id);

alter table "public"."profiles_to_topics" add constraint "profiles_to_topics_pkey" PRIMARY KEY using index "profiles_to_topics_pkey";


