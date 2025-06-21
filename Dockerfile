FROM ghcr.io/trungnguyen1409/openeu-backend-base-image@sha256:e7eaf2a0db55b5723b470e25ec5d3ab76c17947802d51fbb71baa088def605e1

WORKDIR /code
ENV POETRY_VIRTUALENVS_CREATE=false

# Only copy what's needed for fast rebuild
COPY . .

EXPOSE 3000


CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--log-config", "log_conf.yaml", "--reload"]
