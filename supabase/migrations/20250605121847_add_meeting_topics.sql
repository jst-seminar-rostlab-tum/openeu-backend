create table "public"."meeting_topics" (
    "id" text not null default (gen_random_uuid())::text,
    "topic" text not null
);


