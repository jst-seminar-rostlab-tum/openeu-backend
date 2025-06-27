-- migrate:up
alter table "public"."legislative_files" add column if not exists "details_link" text;
alter table "public"."legislative_files" add column if not exists "status" text;
alter table "public"."legislative_files" add column if not exists "subjects" jsonb;
alter table "public"."legislative_files" add column if not exists "key_players" jsonb;
alter table "public"."legislative_files" add column if not exists "key_events" jsonb;
alter table "public"."legislative_files" add column if not exists "documentation_gateway" jsonb;

