create or replace function public.get_meetings_filtered(
    start_time timestamptz default null,
    end_time timestamptz default null,
    topic_ids text[] default null,
    result_limit integer default 100
)
returns setof v_meetings
language sql
as $$
select vm.*
from v_meetings vm
    left join meeting_topic_assignments mta
    on vm.source_id = mta.source_id and vm.source_table = mta.source_table
where
    (start_time is null or vm.meeting_start_datetime >= start_time)
and
    (end_time is null or vm.meeting_start_datetime <= end_time)
and
    (topic_ids is null or mta.topic_id = any(topic_ids))
order by vm.meeting_start_datetime desc
    limit result_limit
$$;
