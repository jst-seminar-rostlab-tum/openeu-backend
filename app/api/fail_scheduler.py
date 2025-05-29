from fastapi import APIRouter

from app.core.scheduling import scheduler

router = APIRouter()


@router.post("/test-failing-job")
async def trigger_failing_job():
    def failing_job():
        raise Exception("Test error for email notification")

    # Register and run the job
    scheduler.register("test_failing_job", failing_job, interval_minutes=10)
    scheduler.run_job("test_failing_job")

    return {"message": "Failing job triggered"}
