FROM trungnguyen1409/openeu-base@sha256:36aa60feb36858512eff2a614a6364b690e5a3d250035c3648353619d3b6435b

WORKDIR /code

ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_NO_INTERACTION=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root

COPY . .

# Optional: remove dev artifacts (e.g. tests, examples)
RUN rm -rf tests/ examples/ notebooks/

EXPOSE 3000

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--log-config", "log_conf.yaml", "--reload"]

# Add the migration command as a separate step
#CMD ["bash", "-c", "npx supabase migration up --db-url postgresql://supabase_admin:${POSTGRES_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME} --debug && poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --log-config log_conf.yaml --reload"]