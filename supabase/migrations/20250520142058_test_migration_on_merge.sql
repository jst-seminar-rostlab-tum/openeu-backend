create table public.test_migration_on_merge (
     id uuid primary key default gen_random_uuid(),
     name text not null,
     created_at timestamp with time zone default timezone('utc'::text, now())
);