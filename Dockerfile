FROM python:3.13.3-slim

WORKDIR /code

#Install supabase
RUN apt-get update && apt-get upgrade -y
RUN apt-get install wget -y
RUN wget -O supabase.deb https://github.com/supabase/cli/releases/download/v2.23.4/supabase_2.23.4_linux_amd64.deb
RUN dpkg -i supabase.deb
RUN rm supabase.deb
RUN supabase --version

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