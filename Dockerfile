FROM python:3.13.3-slim

WORKDIR /code
#RUN apt-get update && apt-get upgrade -y
#RUN apt-get install nodejs npm -y
#RUN npx --yes supabase --version
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libnss3 libgdk-pixbuf2.0-0 libgtk-3-0 libx11-xcb1 \
    libxcomposite1 libxdamage1 libxrandr2 libasound2 libxss1 \
    libxtst6 libxshmfence1 libgbm1 libpango-1.0-0 libatk1.0-0 \
    libatk-bridge2.0-0 libx11-dev libxext6 libxfixes3 libxrender1 \
    libxv1 libxv-dev libdrm2 libxcb1 libopus0 libvpx7 libwoff1 \
    libflite1 libgstreamer-plugins-base1.0-0 gstreamer1.0-plugins-base \
    libgstreamer-plugins-good1.0-0 gstreamer1.0-libav libgraphene-1.0-0 \
    libgtk-4-1 libenchant-2-2 libbhyphen0 libx264-160 \
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