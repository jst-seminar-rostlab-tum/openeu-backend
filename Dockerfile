FROM python:3.13.3-slim

WORKDIR /code
#RUN apt-get update && apt-get upgrade -y
#RUN apt-get install nodejs npm -y
#RUN npx --yes supabase --version
RUN apt-get update && apt-get upgrade -y && \
    apt-get install -y \
    curl gnupg wget unzip xvfb nodejs npm \
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 \
    libxkbcommon0 libatspi2.0-0 libxdamage1 libpango-1.0-0 \
    libcairo2 libasound2 libsecret-1-0 libgles2 \
    libgtk-3-0 libgdk-pixbuf2.0-0 libpangocairo-1.0-0 libcairo-gobject2 \
    libgtk-3-dev libglib2.0-dev \
    && apt-get clean

RUN npx --yes supabase --version
#Install necessary packages & libraries
RUN pip install poetry==2.1.3
RUN pip install playwright
RUN pip install crawl4ai

COPY . .

RUN poetry install
# Install Playwright browsers
#RUN playwright install --with-deps
RUN poetry run playwright install

# Run crawl4ai setup
RUN crawl4ai-setup
RUN mkdir /.script
RUN echo "#!/bin/sh" > /.script/start.sh
RUN echo "cd /code" >> /.script/start.sh
#RUN echo 'npx supabase migration up --db-url postgresql://supabase_admin:${POSTGRES_PASSWORD}@${DB_HOST}:${DB_PORT}/${DB_NAME} --debug' >> /.script/start.sh
RUN echo "poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --log-config log_conf.yaml --reload" >> /.script/start.sh
RUN chmod +x /.script/start.sh

#Expose port
EXPOSE 3000
RUN echo "✅ Checking Playwright..."
RUN playwright --version && which playwright && ls -l $(which playwright)
RUN echo "✅ Checking crawl4ai..."
RUN crawl4ai-doctor

RUN poetry run python healthcheck.py


ENTRYPOINT ["/.script/start.sh"]