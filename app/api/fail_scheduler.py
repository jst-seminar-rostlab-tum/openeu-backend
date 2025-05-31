from fastapi import APIRouter

from app.core.scheduling import scheduler

router = APIRouter()


@router.post("/test-failing-job")
async def trigger_failing_job():
    def failing_job():
        raise Exception("Test error for email notification")

    scheduler.register("test_failing_job", failing_job, interval_minutes=10)
    return {"message": "Failing job registered"}
