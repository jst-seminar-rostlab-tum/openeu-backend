from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

from app.api import profile
from app.api.chat import router as api_chat
from app.api.crawler import router as api_crawler
from app.api.meetings import router as api_meetings
from app.api.notifications import router as notifications_router
from app.api.scheduler import router as api_scheduler
from app.api.topics import router as api_topics
from app.api.suggestions import router as api_suggestions

from app.core.config import Settings
from app.core.jobs import setup_scheduled_jobs

setup_scheduled_jobs()
settings = Settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logging.getLogger("httpcore").setLevel(logging.INFO)
logging.getLogger("httpx").setLevel(logging.INFO)
logging.getLogger("asyncio").setLevel(logging.INFO)

app = FastAPI()
app.include_router(profile.router)
app.include_router(api_meetings)
app.include_router(api_crawler)
app.include_router(api_scheduler)
app.include_router(api_chat)
app.include_router(api_topics)

app.include_router(notifications_router)
app.include_router(api_suggestions)


class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        is_allowed_origin = origin and (
            origin.startswith("http://localhost")
            or origin.endswith("openeu.netlify.app")
            or origin.endswith("openeu.csee.tech")
        )

        if request.method == "OPTIONS" and is_allowed_origin:
            response = PlainTextResponse("Preflight OK", status_code=200)
        else:
            response = await call_next(request)

        if is_allowed_origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS,PATCH"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"

        return response


app.add_middleware(CustomCORSMiddleware)


@app.get("/")
async def root() -> dict[str, str | bool]:
    return {
        "git_branch": settings.get_git_branch(),
        "git_is_pr": settings.is_pull_request(),
        "supabase_host": settings.get_supabase_project_url(),
    }
