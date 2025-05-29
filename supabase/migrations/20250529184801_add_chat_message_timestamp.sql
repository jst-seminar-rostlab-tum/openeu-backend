alter table "public"."chat_messages" drop column "thread_id";

alter table "public"."chat_messages" add column "date" timestamp with time zone;


