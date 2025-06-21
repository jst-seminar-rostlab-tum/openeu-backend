FROM trungnguyen1409/openeu-base@sha256:36037cbb9ee30302e7152cf814b62c2aa217affe41d93091975e1627d174189f

WORKDIR /code

ENV POETRY_VIRTUALENVS_CREATE=false

# Only copy what's needed for fast rebuild
COPY . .

EXPOSE 3000


CMD ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "3000", "--log-config", "log_conf.yaml", "--reload"]
