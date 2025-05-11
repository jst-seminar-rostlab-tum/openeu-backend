# openeu-backend

## Installing dependencies
- Run ```pip install .``` in root directory
- Run ```pre-commit install```

## Database Schemas
- First, install the Supabase CLI as described [here](https://supabase.com/docs/guides/local-development/cli/getting-started#installing-the-supabase-cli)
- Start Docker on your computer
- Generate a migration file by calling ```supabase db diff -f MIGRATION_NAME```
- Stop all local instances of Supabase and then apply the migration by calling ```supabase start && supabase migration up```
- Push the changes to the remote Supabase instance by calling ```supabase db push```

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

The application is hosted on Render, and the latest version of the backend can be accessed at: ```https://openeu-backend.onrender.com```

### Background Jobs
In our project, each background job is associated with a dedicated API endpoint. 
When the corresponding endpoint is triggered, the background job is executed.
We use [cron-job](https://console.cron-job.org/) to automate this process, which invokes these endpoints at predefined intervals.

If you add a new background job, please make sure to: 
- protect the endpoint using the `get_token_header` function from [dependencies.py](./app/dependencies.py) (an example can be found [here](./app/api/crawler.py))
- after adding the cronjob, also add it to the status page [here](https://console.cron-job.org/statuspages/26586)