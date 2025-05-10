# openeu-backend

## Installing dependencies
- Run ```pip install .``` in root directory
- Run ```pre-commit install```

## Database Schemas
- First, install the Supabase CLI as described [here](https://supabase.com/docs/guides/local-development/cli/getting-started#installing-the-supabase-cli)
- Start Docker on your computer
- Generate a migration file by calling ```supabase db diff -f MIGRATION_NAME```
- Stop all local instances of Supabase and then apply the migration by calling ```supabase start && supabase migration up```
- Push the changes to the remote Supabase instance by calling ```supabase db push```