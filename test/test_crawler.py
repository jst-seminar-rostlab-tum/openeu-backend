from app.core.scheduling import scheduler


def test_failing_job_sends_email():
    # Define a job that will fail
    def failing_job():
        raise Exception("Test error for email notification")

    # Register the failing job
    scheduler.register("test_failing_job", failing_job, interval_minutes=10)

    # Run the job - this should trigger the email
    scheduler.run_job("test_failing_job")

    # Note: Since the email sending is asynchronous, you might want to add a small delay
    # to ensure the email is sent before the test completes
    import time

    time.sleep(2)  # Wait for 2 seconds to allow email sending to complete
