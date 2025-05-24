FROM python:3.13.3-bullseye

#Install necessary packages & libraries
RUN pip install poetry==2.1.3
COPY . .
RUN poetry install

#Expose port
EXPOSE 8000



ENTRYPOINT ["poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0"]