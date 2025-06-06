alter table "public"."legislative_files" add column "scraped_at" timestamp with time zone not null default now();

alter table "public"."legislative_files" alter column "lastpubdate" drop not null;

alter table "public"."legislative_files" alter column "link" drop not null;

alter table "public"."legislative_files" alter column "title" drop not null;

alter table "public"."scheduled_job_runs" alter column "last_run_at" drop default;

alter table "public"."scheduled_job_runs" alter column "name" drop not null;


