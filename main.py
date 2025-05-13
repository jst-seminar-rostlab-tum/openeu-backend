from fastapi import FastAPI

from app.api.crawler import router as api_crawler
from app.api.meetings import router as api_meetings

app = FastAPI()
app.include_router(api_meetings)
app.include_router(api_crawler)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
