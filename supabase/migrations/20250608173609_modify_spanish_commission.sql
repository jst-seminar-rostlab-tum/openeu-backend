alter table "public"."spanish_commission_meetings" drop column "description_en";

alter table "public"."spanish_commission_meetings" drop column "location_en";

alter table "public"."spanish_commission_meetings" drop column "title_en";

alter table "public"."spanish_commission_meetings" add column "description_english" text;

alter table "public"."spanish_commission_meetings" add column "location_english" text;

alter table "public"."spanish_commission_meetings" add column "title_english" text;


