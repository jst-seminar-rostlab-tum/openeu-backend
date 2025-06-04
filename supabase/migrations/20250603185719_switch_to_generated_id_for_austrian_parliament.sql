alter table "public"."austrian_parliament_meetings" alter column "id" set default (gen_random_uuid())::text;

CREATE UNIQUE INDEX austrian_parliament_meetings_title_meeting_type_meeting_dat_key ON public.austrian_parliament_meetings USING btree (title, meeting_type, meeting_date, meeting_location);

alter table "public"."austrian_parliament_meetings" add constraint "austrian_parliament_meetings_title_meeting_type_meeting_dat_key" UNIQUE using index "austrian_parliament_meetings_title_meeting_type_meeting_dat_key";


