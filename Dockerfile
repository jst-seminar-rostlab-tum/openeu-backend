FROM trungnguyen1409/openeu-base@sha256:cb953a4979bfa770ea56231e4068c9e76022c9bc3bb4682a97e654299d70a22a

WORKDIR /code

#ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_NO_INTERACTION=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root


COPY . .

#remove dev artifacts (e.g. tests, examples)
RUN rm -rf tests/ examples/ notebooks/

RUN echo "✅ Checking Playwright..."
RUN playwright --version && which playwright && ls -l $(which playwright)
RUN echo "✅ Checking crawl4ai..."
RUN crawl4ai-doctor

#RUN poetry run python healthcheck.py

EXPOSE 3000


CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--log-config", "log_conf.yaml", "--reload"]

# Add the migration command as a separate step
#CMD ["bash", "-c", "npx supabase migration up --db-url postgresql://supabase_admin:${POSTGRES_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME} --debug && poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --log-config log_conf.yaml --reload"]
