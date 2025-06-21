FROM trungnguyen1409/openeu-base:latest

WORKDIR /code

COPY . .

# Add any lightweight app-only steps
RUN mkdir /.script
RUN echo "#!/bin/sh" > /.script/start.sh
RUN echo "cd /code" >> /.script/start.sh

RUN echo "poetry run uvicorn main:app --host 0.0.0.0 --port 3000 --log-config log_conf.yaml --reload" >> /.script/start.sh
RUN chmod +x /.script/start.sh

EXPOSE 3000
RUN echo "✅ Checking Playwright..."
RUN playwright --version && which playwright && ls -l $(which playwright)
RUN echo "✅ Checking crawl4ai..."
RUN crawl4ai-doctor

RUN poetry run python healthcheck.py


ENTRYPOINT ["/.script/start.sh"]
