# === Stage 1: Dependency Builder ===
FROM python:3.13-slim AS builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_NO_INTERACTION=1

# Install system deps & Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget unzip build-essential && \
    pip install --no-cache-dir poetry==2.1.3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Enable in-project virtualenvs
ENV POETRY_VIRTUALENVS_CREATE=true
RUN poetry config virtualenvs.in-project true

# Copy dependency definitions only
COPY pyproject.toml poetry.lock* ./

# Install only main dependencies into .venv
RUN poetry install --only main --no-root

# === Stage 2: Runtime ===
FROM trungnguyen1409/openeu-base@sha256:22b8522a91d1341bf7609db757e7a507aa2822ba0e059295dc21a28fedcb2f94

# Health checks (optional)
RUN echo "✅ Checking Playwright..." && \
    playwright --version && \
    echo "✅ Checking Crawl4AI..." && \
    crawl4ai-doctor || echo "⚠️  Crawl4AI doctor failed – this may be expected on certain hosts"

WORKDIR /code

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/code/.venv/bin:$PATH" \
    VIRTUAL_ENV="/code/.venv"

# Copy installed virtual environment from builder
COPY --from=builder /app/.venv /code/.venv
COPY --from=builder /app/poetry.lock /code/
COPY --from=builder /app/pyproject.toml /code/

# Copy app source code
COPY . .

# Optional: Clean dev stuff not already ignored by .dockerignore
RUN rm -rf tests/ examples/ notebooks/ .git __pycache__

# Health checks (optional)
RUN echo "✅ Checking Playwright..." && \
    playwright --version && \
    echo "✅ Checking Crawl4AI..." && \
    crawl4ai-doctor || echo "⚠️  Crawl4AI doctor failed – this may be expected on certain hosts"

EXPOSE 3000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--log-config", "log_conf.yaml", "--reload"]
