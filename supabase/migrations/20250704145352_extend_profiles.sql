create type "public"."user_type_enum" as enum ('entrepreneur', 'politician');

create table "public"."companies" (
    "id" uuid not null default gen_random_uuid(),
    "role" text not null,
    "name" text not null,
    "description" text not null,
    "company_stage" text not null,
    "company_size" integer not null,
    "industry" text not null
);


create table "public"."politicians" (
    "id" uuid not null default gen_random_uuid(),
    "role" text not null,
    "further_information" text,
    "institution" text not null,
    "area_of_expertise" text not null
);


alter table "public"."profiles" drop column "company_description";

alter table "public"."profiles" drop column "company_name";

alter table "public"."profiles" add column "company_id" uuid;

alter table "public"."profiles" add column "politician_id" uuid;

alter table "public"."profiles" add column "user_type" user_type_enum not null;

CREATE UNIQUE INDEX companies_pkey ON public.companies USING btree (id);

CREATE UNIQUE INDEX politicians_pkey ON public.politicians USING btree (id);

alter table "public"."companies" add constraint "companies_pkey" PRIMARY KEY using index "companies_pkey";

alter table "public"."politicians" add constraint "politicians_pkey" PRIMARY KEY using index "politicians_pkey";

alter table "public"."profiles" add constraint "profiles_company_id_fkey" FOREIGN KEY (company_id) REFERENCES companies(id) ON DELETE CASCADE not valid;

alter table "public"."profiles" validate constraint "profiles_company_id_fkey";

alter table "public"."profiles" add constraint "profiles_politician_id_fkey" FOREIGN KEY (politician_id) REFERENCES politicians(id) ON DELETE CASCADE not valid;

alter table "public"."profiles" validate constraint "profiles_politician_id_fkey";

grant delete on table "public"."companies" to "anon";

grant insert on table "public"."companies" to "anon";

grant references on table "public"."companies" to "anon";

grant select on table "public"."companies" to "anon";

grant trigger on table "public"."companies" to "anon";

grant truncate on table "public"."companies" to "anon";

grant update on table "public"."companies" to "anon";

grant delete on table "public"."companies" to "authenticated";

grant insert on table "public"."companies" to "authenticated";

grant references on table "public"."companies" to "authenticated";

grant select on table "public"."companies" to "authenticated";

grant trigger on table "public"."companies" to "authenticated";

grant truncate on table "public"."companies" to "authenticated";

grant update on table "public"."companies" to "authenticated";

grant delete on table "public"."companies" to "service_role";

grant insert on table "public"."companies" to "service_role";

grant references on table "public"."companies" to "service_role";

grant select on table "public"."companies" to "service_role";

grant trigger on table "public"."companies" to "service_role";

grant truncate on table "public"."companies" to "service_role";

grant update on table "public"."companies" to "service_role";

grant delete on table "public"."politicians" to "anon";

grant insert on table "public"."politicians" to "anon";

grant references on table "public"."politicians" to "anon";

grant select on table "public"."politicians" to "anon";

grant trigger on table "public"."politicians" to "anon";

grant truncate on table "public"."politicians" to "anon";

grant update on table "public"."politicians" to "anon";

grant delete on table "public"."politicians" to "authenticated";

grant insert on table "public"."politicians" to "authenticated";

grant references on table "public"."politicians" to "authenticated";

grant select on table "public"."politicians" to "authenticated";

grant trigger on table "public"."politicians" to "authenticated";

grant truncate on table "public"."politicians" to "authenticated";

grant update on table "public"."politicians" to "authenticated";

grant delete on table "public"."politicians" to "service_role";

grant insert on table "public"."politicians" to "service_role";

grant references on table "public"."politicians" to "service_role";

grant select on table "public"."politicians" to "service_role";

grant trigger on table "public"."politicians" to "service_role";

grant truncate on table "public"."politicians" to "service_role";

grant update on table "public"."politicians" to "service_role";


