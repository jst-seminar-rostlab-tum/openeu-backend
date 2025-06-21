FROM ghcr.io/jst-seminar-rostlab-tum/openeu-base-image@sha256:e1d6167c78ce8b3bd6cd5f264351cb346632b555b275d1969b5cac2c7aef0d62

WORKDIR /code
ENV POETRY_VIRTUALENVS_CREATE=false

# Only copy what's needed for fast rebuild
COPY . .

EXPOSE 3000


CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--log-config", "log_conf.yaml", "--reload"]
