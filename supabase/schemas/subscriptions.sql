create table if not exists public.subscriptions (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null,
    legislation_id text not null references public.legislative_files(id),
    created_at timestamp with time zone default now()
);
