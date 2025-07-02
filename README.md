# ProjectEurope - OpenEU - Backend

<!-- ALL-CONTRIBUTORS-BADGE:START - Do not remove or modify this section -->

[![All Contributors](https://img.shields.io/badge/all_contributors-16-orange.svg?style=flat-square)](#contributors-)

<!-- ALL-CONTRIBUTORS-BADGE:END -->

## 📘 Swagger UI & OpenAPI Docs

You can test and explore the API via:

- 🧪 Swagger UI: https://openeu-backend-1.onrender.com/docs
- 📕 ReDoc: https://openeu-backend-1.onrender.com/redoc
- 🧾 OpenAPI JSON: https://openeu-backend-1.onrender.com/openapi.json

## 📦 Project Structure

```
openeu-backend/
├── app/
│   ├── api/
│   │   └── meetings.py              # REST API endpoints using FastAPI
│   ├── core/
│   │   ├── config.py              # Loads environment variables, has a Settings class that contains all env vars we need
│   │   └── supabase_client.py     # Initializes Supabase client
│   ├── data_sources/
│   │   ├── scrapers/
│   │   │   └── site1-scraper.py           # Scraper for website 1
│   │   ├── apis/
│   │   │   └── source1_api.py     # Fetcher for API-based source 1
│   │   └── task_runner.py        # Aggregates all sources (scrapers + APIs)
├── scripts/
│   └── run_job.py               # script for running task_runner
├── supabase/
│   ├── schemas/
│   │   ├── meetings.sql
├── main.py                        # FastAPI application entrypoint
├── .gitignore
├── .env
├── pyproject.toml                  # Poetry configuration file
└── README.md
```

## Developer environment
The development environment is containerized using Docker.

### Prerequisites
#### Docker Desktop
Make sure you have Docker Desktop installed. You can download it from the official site: [Docker Desktop](https://www.docker.com/products/docker-desktop/).
#### .env
Make sure to create a `.env` file before starting the developer environment. For local development copy the content of `.env.example`.

### Starting the Environment
To start the environment, run:
```
docker-compose up -d
```
This command starts the containers in detached mode.

### Stopping the Environment
To stop and remove the containers, run:
```
docker-compose down
```
### ⚠️ Important: Add/Remove Python Packages
If you add or update any packages in the project, you'll need to rebuild the Docker image to ensure the environment reflects those changes. To rebuild, use:
```
docker-compose build
```

## Installing dependencies
This project uses Poetry for dependency management and packaging. So in order to install all dependencies, you need to install Poetry first. To do so, follow these steps:
- Install pipx on your computer as described [here](https://pipx.pypa.io/stable/installation/)
- Install Poetry by running ```pipx install poetry```

After that, you can install the dependencies of this project:
```
poetry install
```

This command creates a virtual environment (if one doesn’t exist) and installs all dependencies defined in pyproject.toml. 

After that, complete the setup for crawl4ai which is needed for the MEC meetings scraper (installs/updates Playwright browsers, checks for missing OS libs, etc.):

```
crawl4ai-setup
```

To run the project, run 
```
poetry run uvicorn main:app --reload --log-config log_conf.yaml
```

In order to activate pre commit hooks, you need to run the following command:
```
pre-commit install
```

If you want to install dependencies from `requirements.txt`, you can generate it using:
```
poetry export --without-hashes --format=requirements.txt --output requirements.txt
```

## Database Schemas
The database schema is defined inside this project and must be pushed to Supabase once 
- First, install the Supabase CLI as described [here](https://supabase.com/docs/guides/local-development/cli/getting-started#installing-the-supabase-cli)
- Start Docker on your computer
- merge main into your branch
- if you have new tables, that don't exist on remote
  - 1. stop your local supabase `supabase stop`
  - 2. generate new migration with your changes `supabase db diff -f migration_name`
  - 3. `supabase start`
  - 4. reset local db to new schema `supabase db reset`
- never push with `supabase db push`, from now on we only generate migrations locally, but the pushing happens in the pipeline when we merge to main
- never add tables or views in the remote supabase console. Only use the declarative schema
- never edit migration files, only the schema itself

## Testing the Crawler endpoint
In order to test the `crawler` endpoint you need to do the following: 
 - First assign `CRAWLER_API_KEY` an arbitrary string in the `.env` file
 - Prepare a `GET` request in [Postman](https://www.postman.com/downloads/) to `localhost:8000/crawler/`
 - Navigate in Postman to the Headers Tab
 - Add a new header 
   - Key: `token` 
   - Value: The same value you set for `CRAWLER_API_KEY` in your `.env` file 
 - Send the request

## Backend Deployment
The deployment of our backend application is fully automated using GitHub Actions.
Each time a commit is pushed to the main branch, a deployment workflow is triggered to ensure that the latest changes are live without manual intervention.

The application is hosted on Render, and the latest version of the backend can be accessed at: ```https://openeu-backend-1.onrender.com```

### Environment Variables
Please ensure that you added all necessary environment variables to production before pushing to main.
You can add the environment variables for production [here](https://dashboard.render.com/web/srv-d0vdf7vfte5s739i276g/env).

## Background Jobs
In our project, each background job is associated with a dedicated API endpoint. 
When the corresponding endpoint is triggered, the background job is executed.
We use [cron-job](https://console.cron-job.org/) to automate this process, which invokes these endpoints at predefined intervals.

If you add a new background job, please make sure to: 
- protect the endpoint using the `get_token_header` function from [dependencies.py](./app/dependencies.py) (an example can be found [here](./app/api/crawler.py))
- after adding the cronjob, also add it to the status page [here](https://console.cron-job.org/statuspages/26586)



## Testing Email  - Sending Emails: Local Development & Production Safety
You can safely test email functionality during local development without sending real emails. To enable local email testing, add these variables to your .env file:

```
EMAIL_BACKEND=local_dev_only_smtp
ENVIRONMENT=development
EMAIL_HOST=localhost
EMAIL_PORT=1025
```
**How it works:**
- Local development: Emails are sent to your local SMTP server (such as Mailpit or MailHog). No real users will ever receive test messages.
- All other environments: If these variables are missing, or if you’re running in staging or production, the system automatically uses the Brevo transactional email API and sends real emails using the API key in your environment.
- Fallback behavior: If ENVIRONMENT=development but EMAIL_BACKEND is missing or not set to local_dev_only_smtp, emails are logged to the console (as before), and are not sent.

Summary:
- Local: Use EMAIL_BACKEND=local_dev_only_smtp and ENVIRONMENT=development to safely test emails using mailpit
- Production: Remove or change these variables (ENVIRONMENT=development, EMAIL_BACKEND=local_dev_only_smtp) to use Brevo and send real emails.
- ENVIRONMENT=development -> logging email as before