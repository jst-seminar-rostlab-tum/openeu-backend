from fastapi import FastAPI

from app.api.crawler import router as api_crawler
from app.api.meetings import router as api_meetings
from app.api.scheduler import router as api_scheduler
from app.core.jobs import setup_scheduled_jobs

setup_scheduled_jobs()

app = FastAPI()
app.include_router(api_meetings)
app.include_router(api_crawler)
app.include_router(api_scheduler)
