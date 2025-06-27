alter table "public"."legislative_files" add column "embedding_input" text;
alter table "public"."legislative_files" rename column "reference" to "id";
