FROM python:3.13.3-slim

WORKDIR /code

#Install supabase
# System deps
RUN apt-get update && apt-get install -y \
    curl gnupg wget unzip xvfb nodejs npm \
    libnss3 libatk1.0-0 libatk-bridge2.0-0 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 libgbm1 libgtk-3-0 \
    libasound2 libxshmfence1 libxext6 libxfixes3 libxrender1 \
    libx11-6 libxtst6 libglib2.0-0 libpci3 libdrm2 \
    libenchant-2-2 libsecret-1-0 libmanette-0.2-0 libgles2 \
    && apt-get clean

# Install Supabase CLI + Playwright CLI
RUN npm install -g supabase playwright

#Install necessary packages & libraries
RUN pip install poetry==2.1.3
COPY pyproject.toml .
#COPY .env .env
COPY README.md README.md
COPY app app

RUN poetry install

# Install Playwright browsers
RUN playwright install

# Run crawl4ai setup
RUN poetry run crawl4ai-setup

RUN mkdir /.script
RUN echo "#!/bin/sh" > /.script/start.sh
RUN echo "cd /code" >> /.script/start.sh
RUN echo "npx supabase migration up --db-url postgresql://supabase_admin:\${POSTGRES_PASSWORD}@\${DB_HOST}:\${DB_PORT}/\${DB_NAME} --debug" >> /.script/start.sh
RUN echo "poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --log-config log_conf.yaml --reload" >> /.script/start.sh
RUN chmod +x /.script/start.sh


#Expose port
EXPOSE 3000
ENTRYPOINT ["/.script/start.sh"]