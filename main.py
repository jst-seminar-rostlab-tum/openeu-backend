from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging
import re
from fastapi.responses import JSONResponse

from app.api import profile
from app.api.chat import router as api_chat
from app.api.crawler import router as api_crawler
from app.api.meetings import router as api_meetings
from app.api.legislative_files import router as api_legislative_files  # <- make sure this import is correct
from app.api.notifications import router as notifications_router
from app.api.alerts import router as api_alerts
from app.api.scheduler import router as api_scheduler
from app.api.topics import router as api_topics
from app.core.auth import decode_supabase_jwt, User


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
logging.getLogger("hpack").setLevel(logging.INFO)

app = FastAPI()
app.include_router(profile.router)
app.include_router(api_meetings)
app.include_router(api_crawler)
app.include_router(api_scheduler)
app.include_router(api_chat)
app.include_router(api_topics)
app.include_router(api_legislative_files)

app.include_router(notifications_router)
app.include_router(api_alerts)


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


class JWTMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.public_paths = [r"^/$", r"^/docs$", r"^/redoc$", r"^/openapi.json$", r"^/scheduler/tick", r"^/topics"]

    async def dispatch(self, request: Request, call_next):
        if request.method == "OPTIONS":
            return await call_next(request)

        for pattern in self.public_paths:
            if re.match(pattern, request.url.path):
                response = await call_next(request)
                return response

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authentication required. Missing Authorization header."},
                headers={"WWW-Authenticate": "Bearer"},
            )

        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authentication scheme. Must be Bearer.")

            payload = decode_supabase_jwt(token)
            # Store the decoded user information in request.state
            # This makes the user object available to any endpoint via `request.state.user`
            # or through the `get_current_user` dependency.
            request.state.user = User(id=payload.get("sub"), email=payload.get("email"))

        except (ValueError, HTTPException) as e:
            detail = getattr(e, "detail", str(e))

            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": f"Invalid authentication token: {detail}"},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except Exception as e:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": f"An unexpected error occurred during authentication: {e}"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        response = await call_next(request)
        return response


app.add_middleware(JWTMiddleware)


@app.get("/")
async def root() -> dict[str, str | bool]:
    return {
        "git_branch": settings.get_git_branch(),
        "git_is_pr": settings.is_pull_request(),
        "supabase_host": settings.get_supabase_project_url(),
    }
