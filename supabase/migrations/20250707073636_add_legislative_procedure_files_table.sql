create table "public"."legislative_procedure_files" (
    "id" text not null,
    "link" text not null,
    "extracted_text" text not null,
    "scraped_at" timestamp with time zone not null default now()
);


CREATE UNIQUE INDEX legislative_procedure_files_pkey ON public.legislative_procedure_files USING btree (id);

alter table "public"."legislative_procedure_files" add constraint "legislative_procedure_files_pkey" PRIMARY KEY using index "legislative_procedure_files_pkey";

grant delete on table "public"."legislative_procedure_files" to "anon";

grant insert on table "public"."legislative_procedure_files" to "anon";

grant references on table "public"."legislative_procedure_files" to "anon";

grant select on table "public"."legislative_procedure_files" to "anon";

grant trigger on table "public"."legislative_procedure_files" to "anon";

grant truncate on table "public"."legislative_procedure_files" to "anon";

grant update on table "public"."legislative_procedure_files" to "anon";

grant delete on table "public"."legislative_procedure_files" to "authenticated";

grant insert on table "public"."legislative_procedure_files" to "authenticated";

grant references on table "public"."legislative_procedure_files" to "authenticated";

grant select on table "public"."legislative_procedure_files" to "authenticated";

grant trigger on table "public"."legislative_procedure_files" to "authenticated";

grant truncate on table "public"."legislative_procedure_files" to "authenticated";

grant update on table "public"."legislative_procedure_files" to "authenticated";

grant delete on table "public"."legislative_procedure_files" to "service_role";

grant insert on table "public"."legislative_procedure_files" to "service_role";

grant references on table "public"."legislative_procedure_files" to "service_role";

grant select on table "public"."legislative_procedure_files" to "service_role";

grant trigger on table "public"."legislative_procedure_files" to "service_role";

grant truncate on table "public"."legislative_procedure_files" to "service_role";

grant update on table "public"."legislative_procedure_files" to "service_role";


