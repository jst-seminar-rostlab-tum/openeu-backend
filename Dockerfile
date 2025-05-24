FROM python:3.13.3-slim

WORKDIR /code

#Install necessary packages & libraries
RUN pip install poetry==2.1.3
COPY pyproject.toml .
COPY .env .env
COPY README.md README.md
COPY app app

RUN poetry install

#Expose port
EXPOSE 3000