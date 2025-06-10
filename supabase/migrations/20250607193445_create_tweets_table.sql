create table "public"."tweets" (
    "id" text not null,
    "text" text not null,
    "author" jsonb not null,
    "created_at" timestamp with time zone not null,
    "reply_count" integer default 0,
    "view_count" integer default 0,
    "like_count" integer default 0,
    "quote_count" integer default 0,
    "quoted_tweet" jsonb,
    "retweeted_tweet" jsonb,
    "scraped_at" timestamp with time zone not null default now()
);


alter table "public"."scheduled_job_runs" alter column "last_run_at" drop default;

alter table "public"."scheduled_job_runs" alter column "name" drop not null;

CREATE UNIQUE INDEX tweets_pkey ON public.tweets USING btree (id);

alter table "public"."tweets" add constraint "tweets_pkey" PRIMARY KEY using index "tweets_pkey";

grant delete on table "public"."tweets" to "anon";

grant insert on table "public"."tweets" to "anon";

grant references on table "public"."tweets" to "anon";

grant select on table "public"."tweets" to "anon";

grant trigger on table "public"."tweets" to "anon";

grant truncate on table "public"."tweets" to "anon";

grant update on table "public"."tweets" to "anon";

grant delete on table "public"."tweets" to "authenticated";

grant insert on table "public"."tweets" to "authenticated";

grant references on table "public"."tweets" to "authenticated";

grant select on table "public"."tweets" to "authenticated";

grant trigger on table "public"."tweets" to "authenticated";

grant truncate on table "public"."tweets" to "authenticated";

grant update on table "public"."tweets" to "authenticated";

grant delete on table "public"."tweets" to "service_role";

grant insert on table "public"."tweets" to "service_role";

grant references on table "public"."tweets" to "service_role";

grant select on table "public"."tweets" to "service_role";

grant trigger on table "public"."tweets" to "service_role";

grant truncate on table "public"."tweets" to "service_role";

grant update on table "public"."tweets" to "service_role";


