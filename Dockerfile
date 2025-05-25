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

RUN poetry install

#Expose port
EXPOSE 3000
ENTRYPOINT ["./start_dev_env.sh"]