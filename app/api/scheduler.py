from fastapi import APIRouter

from app.core.scheduling import scheduler

router = APIRouter(prefix="/scheduler")


@router.get("/")
def run_scheduled_tasks() -> dict[str, str]:
    scheduler.tick()
    return {"message": "Hello World"}
