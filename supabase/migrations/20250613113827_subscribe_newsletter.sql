alter table "public"."profiles" add column "subscribed_newsletter" boolean not null default false;

alter table "public"."tweets" drop column "embedding_input";


