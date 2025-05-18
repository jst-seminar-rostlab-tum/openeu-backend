from fastapi import APIRouter, Response, status

from app.core.scheduling import scheduler

router = APIRouter(prefix="/scheduler")


@router.get("/tick")
def run_scheduled_tasks() -> dict[str, str]:
    scheduler.tick()
    return {"message": "Hello World"}


@router.post("/run/{job_name}")
def run_task(job_name: str, response: Response):
    try:
        scheduler.run_job(job_name)
    except ValueError as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": str(e)}
