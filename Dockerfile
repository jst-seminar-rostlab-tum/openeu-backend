# === Stage 1: Dependency Builder ===
FROM python:3.13-slim AS builder

WORKDIR /app

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies for pip/poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget unzip build-essential && \
    pip install --no-cache-dir poetry==2.1.3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy only dependency descriptors
COPY pyproject.toml poetry.lock* ./

# Install dependencies
RUN poetry install --no-root

# === Stage 2: Runtime ===
FROM trungnguyen1409/openeu-base@sha256:22b8522a91d1341bf7609db757e7a507aa2822ba0e059295dc21a28fedcb2f94

WORKDIR /code

# Copy preinstalled site-packages from builder
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy source code last
COPY . .

# Clean up irrelevant files (if not already `.dockerignore`d)
RUN rm -rf tests/ examples/ notebooks/ .git


RUN echo "✅ Checking Playwright..." && \
    playwright --version && \
    echo "✅ Checking Crawl4AI..." && \
    crawl4ai-doctor || echo "⚠️  Crawl4AI doctor failed – this may be expected on certain hosts"

EXPOSE 3000

CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--log-config", "log_conf.yaml", "--reload"]

# Add the migration command as a separate step
#CMD ["bash", "-c", "npx supabase migration up --db-url postgresql://supabase_admin:${POSTGRES_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME} --debug && poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --log-config log_conf.yaml --reload"]

