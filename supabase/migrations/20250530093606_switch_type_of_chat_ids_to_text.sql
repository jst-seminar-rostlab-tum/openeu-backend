-- 1. drop the foreign key constraint
alter table "public"."chat_messages" drop constraint if exists fk_chat_sessions;
-- 2. alter the columns
alter table "public"."chat_messages" alter COLUMN "chat_session" drop DEFAULT;
alter table "public"."chat_messages" alter COLUMN "chat_session" drop NOT NULL;
alter table "public"."chat_messages" alter COLUMN "chat_session" SET DATA TYPE text USING "chat_session"::text;
alter table "public"."chat_messages" alter COLUMN "id" SET DATA TYPE text USING "id"::text;
alter table "public"."chat_messages" alter COLUMN "id" SET DEFAULT (gen_random_uuid())::text;
alter table "public"."chat_sessions" alter COLUMN "id" SET DATA TYPE text USING "id"::text;
alter table "public"."chat_sessions" alter COLUMN "id" SET DEFAULT (gen_random_uuid())::text;
-- 3. Recreate the foreign key constraint
alter table "public"."chat_messages"
    add constraint fk_chat_sessions
    foreign key ("chat_session")
    references "public"."chat_sessions"("id")
    on delete cascade;
-- 4. drop sequences
drop SEQUENCE if exists "public"."chat_messages_chat_session_seq";
drop SEQUENCE if exists "public"."chat_messages_id_seq";
drop SEQUENCE if exists "public"."chat_sessions_id_seq";
