FROM python:3.13.3-slim

WORKDIR /code

#Install supabase
RUN apt-get update && apt-get upgrade -y
RUN apt-get install nodejs npm -y
RUN npx --yes supabase --version

#Install necessary packages & libraries
RUN pip install poetry==2.1.3
COPY pyproject.toml .
COPY .env .env
COPY README.md README.md
COPY app app

RUN mkdir /.script
RUN echo "#!/bin/sh" > /.script/start.sh
RUN echo "cd /code" >> /.script/start.sh
RUN echo "npx supabase migration up --db-url postgresql://supabase_admin:\${POSTGRES_PASSWORD}@\${DB_HOST}:\${DB_PORT}/\${DB_NAME} --debug" >> /.script/start.sh
RUN echo "poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --log-config log_conf.yaml --reload" >> /.script/start.sh
RUN chmod +x /.script/start.sh

RUN poetry install

#Expose port
EXPOSE 3000
ENTRYPOINT ["/.script/start.sh"]