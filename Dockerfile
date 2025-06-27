# === Stage 1: Dependency Builder ===
FROM python:3.13-slim AS builder

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_NO_INTERACTION=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget unzip build-essential && \
    pip install --no-cache-dir poetry==2.1.3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

ENV POETRY_VIRTUALENVS_CREATE=true
RUN poetry config virtualenvs.in-project true

COPY pyproject.toml poetry.lock* ./
RUN poetry install --only main --no-root

# === Stage 2: Runtime ===
FROM trungnguyen1409/openeu-base@sha256:22b8522a91d1341bf7609db757e7a507aa2822ba0e059295dc21a28fedcb2f94

WORKDIR /code

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    VIRTUAL_ENV="/code/.venv" \
    PATH="/code/.venv/bin:$PATH"

# Copy prebuilt venv + deps
COPY --from=builder /app/.venv /code/.venv
COPY --from=builder /app/poetry.lock /code/
COPY --from=builder /app/pyproject.toml /code/

# Copy app source
COPY . .

# Optional cleanup
RUN rm -rf tests/ examples/ notebooks/ .git __pycache__

# Health check
RUN crawl4ai-doctor || echo "⚠️  Crawl4AI doctor failed – continuing"

EXPOSE 3000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--log-config", "log_conf.yaml", "--reload"]
