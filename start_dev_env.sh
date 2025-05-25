#!/bin/sh
supabase migration up --db-url postgresql://supabase_admin:${POSTGRES_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME} --debug
poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --log-config log_conf.yaml --reload