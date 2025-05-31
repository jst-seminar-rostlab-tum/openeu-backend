from app.core.email import Email, EmailService

DEFAULT_RECIPIENTS = ["dogayasa@gmail.com", "trungnguyenb0k30@gmail.com", "bohdan.garchu@tum.de"]


def notify_job_failure(job_name: str, error: Exception) -> None:
    """
    Build a transactional e-mail and send it via EmailService.

    Keeps the template in one place so ScheduledJob doesn’t need to
    know how alerting works.
    """
    msg = Email(
        subject=f"Job '{job_name}' Failed",
        html_body=(
            f"<p>The job '<strong>{job_name}</strong>' failed with the " f"following error:</p><pre>{error}</pre>"
        ),
        recipients=DEFAULT_RECIPIENTS,
    )
    EmailService.send_email(msg)
