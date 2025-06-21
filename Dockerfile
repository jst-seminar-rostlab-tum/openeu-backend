FROM trungnguyen1409/openeu-base:latest

WORKDIR /code

ENV POETRY_VIRTUALENVS_CREATE=false

# Only copy what's needed for fast rebuild
COPY . .

# Create unified entrypoint script
RUN mkdir -p /.script && \
    echo '#!/bin/sh' > /.script/start.sh && \
    echo 'cd /code' >> /.script/start.sh && \
    echo 'poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --log-config log_conf.yaml --reload' >> /.script/start.sh && \
    chmod +x /.script/start.sh

EXPOSE 3000


ENTRYPOINT ["/.script/start.sh"]
