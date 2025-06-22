drop function if exists "public"."match_filtered_meetings"(src_tables text[], content_columns text[], query_embedding vector, match_count integer);

drop function if exists "public"."match_filtered_meetings"(src_tables text[], content_columns text[], query_embedding vector, match_count integer, allowed_topic_ids text[], allowed_countries text[]);


