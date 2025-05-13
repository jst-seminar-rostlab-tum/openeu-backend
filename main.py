from fastapi import FastAPI

from app.api.meetings import router as api_meetings
from app.api.crawler import router as api_crawler

app = FastAPI()
app.include_router(api_meetings)
app.include_router(api_crawler)
