# === Stage 1: Dependency Builder ===
FROM python:3.13-slim AS builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=true

# Install system dependencies and Poetry
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget unzip build-essential && \
    pip install --no-cache-dir poetry==2.1.3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Enable local .venv
RUN poetry config virtualenvs.in-project true

# Copy dependency descriptors
COPY pyproject.toml poetry.lock* ./

# Install only main dependencies (no dev or source code)
RUN poetry install --only main --no-root && \
    rm -rf ~/.cache/pypoetry ~/.cache/pip

# === Stage 2: Runtime ===
FROM trungnguyen1409/openeu-base@sha256:22b8522a91d1341bf7609db757e7a507aa2822ba0e059295dc21a28fedcb2f94

WORKDIR /code

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV="/code/.venv" \
    PATH="/code/.venv/bin:$PATH"

# Copy prebuilt virtualenv and lockfiles
COPY --from=builder /app/.venv /code/.venv
COPY --from=builder /app/poetry.lock /code/
COPY --from=builder /app/pyproject.toml /code/

# Copy actual source code
COPY . .

# Optional: clean up dev clutter (ensure .dockerignore is solid too)
RUN rm -rf tests/ examples/ notebooks/ .git __pycache__

# Debug sanity check
RUN echo "✅ Checking uvicorn path..." && \
    ls -lah /code/.venv/bin/uvicorn || (echo "❌ uvicorn not found!" && exit 1)

RUN ls -l /code/.venv/bin/uvicorn && \
    head -n1 /code/.venv/bin/uvicorn && \
    /code/.venv/bin/python --version

# Health check for Crawl4AI & Playwright
RUN echo "✅ Checking Playwright..." && \
    playwright --version && \
    echo "✅ Checking Crawl4AI..." && \
    crawl4ai-doctor || echo "⚠️  Crawl4AI doctor failed – continuing"

EXPOSE 3000

CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--log-config", "log_conf.yaml", "--reload"]
