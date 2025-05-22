create table "public"."scheduled_job_runs" (
    "name" character varying(255) not null,
    "last_run_at" timestamp without time zone
);


CREATE UNIQUE INDEX scheduled_job_runs_pkey ON public.scheduled_job_runs USING btree (name);

alter table "public"."scheduled_job_runs" add constraint "scheduled_job_runs_pkey" PRIMARY KEY using index "scheduled_job_runs_pkey";

grant delete on table "public"."scheduled_job_runs" to "anon";

grant insert on table "public"."scheduled_job_runs" to "anon";

grant references on table "public"."scheduled_job_runs" to "anon";

grant select on table "public"."scheduled_job_runs" to "anon";

grant trigger on table "public"."scheduled_job_runs" to "anon";

grant truncate on table "public"."scheduled_job_runs" to "anon";

grant update on table "public"."scheduled_job_runs" to "anon";

grant delete on table "public"."scheduled_job_runs" to "authenticated";

grant insert on table "public"."scheduled_job_runs" to "authenticated";

grant references on table "public"."scheduled_job_runs" to "authenticated";

grant select on table "public"."scheduled_job_runs" to "authenticated";

grant trigger on table "public"."scheduled_job_runs" to "authenticated";

grant truncate on table "public"."scheduled_job_runs" to "authenticated";

grant update on table "public"."scheduled_job_runs" to "authenticated";

grant delete on table "public"."scheduled_job_runs" to "service_role";

grant insert on table "public"."scheduled_job_runs" to "service_role";

grant references on table "public"."scheduled_job_runs" to "service_role";

grant select on table "public"."scheduled_job_runs" to "service_role";

grant trigger on table "public"."scheduled_job_runs" to "service_role";

grant truncate on table "public"."scheduled_job_runs" to "service_role";

grant update on table "public"."scheduled_job_runs" to "service_role";


