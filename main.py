from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.api import profile
from app.api.chat import router as api_chat
from app.api.crawler import router as api_crawler
from app.api.meetings import router as api_meetings
from app.api.scheduler import router as api_scheduler
from app.core.jobs import setup_scheduled_jobs

setup_scheduled_jobs()

app = FastAPI()
app.include_router(profile.router)
app.include_router(api_meetings)
app.include_router(api_crawler)
app.include_router(api_scheduler)
app.include_router(api_chat)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def dynamic_cors_middleware(request: Request, call_next):
    origin = request.headers.get("origin")
    if origin and origin.endswith("openeu.netlify.app"):
        response = await call_next(request)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    return await call_next(request)


@app.get("/")
async def root() -> dict[str, str]:
    return {"message": "Hello World"}
