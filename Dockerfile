# === Stage 1: Dependency Builder ===
FROM python:3.13-slim AS builder

WORKDIR /app

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl wget unzip build-essential && \
    pip install --no-cache-dir poetry==2.1.3 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


# Copy dependency descriptors
COPY pyproject.toml poetry.lock* ./

# Install Python deps only (no app)
RUN poetry install --only main --no-root

# === Stage 2: Runtime Layer ===
FROM trungnguyen1409/openeu-base@sha256:22b8522a91d1341bf7609db757e7a507aa2822ba0e059295dc21a28fedcb2f94

# Validate runtime health
RUN echo "✅ Checking Playwright..." && \
    playwright --version && \
    echo "✅ Checking Crawl4AI..." && \
    crawl4ai-doctor || echo "⚠️  Crawl4AI doctor failed – this may be expected on certain hosts"


WORKDIR /code

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copy site-packages from builder (user deps)
COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy app source code
COPY . .

# Port
EXPOSE 3000

# Start command
CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--log-config", "log_conf.yaml", "--reload"]
