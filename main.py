from fastapi import FastAPI

from app.api.routes import router as api_router
from app.api.crawler import router as api_crawler

app = FastAPI()
app.include_router(api_router)
app.include_router(api_crawler)
