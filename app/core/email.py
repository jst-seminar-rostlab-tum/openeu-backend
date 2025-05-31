import logging
from typing import Optional

import brevo_python
from brevo_python.rest import ApiException

from app.core.config import Settings


class Email:
    """
    Simple container for an outbound transactional e-mail.
    """

    def __init__(
        self,
        *,
        subject: str,
        html_body: str,
        recipients: list[str],
        text_body: Optional[str] = None,
        sender_name: str = "OpenEU",
        sender_email: str = "mail@openeu.csee.tech",
        reply_to: Optional[str] = None,
        headers: Optional[dict[str, str]] = None,
    ):
        self.subject = subject
        self.html_body = html_body
        self.text_body = text_body
        self.recipients = recipients
        self.sender_name = sender_name
        self.sender_email = sender_email
        self.reply_to = reply_to
        self.headers = headers or {}


class EmailService:
    logger = logging.getLogger(__name__)
    settings = Settings()
    configuration = brevo_python.Configuration()
    configuration.api_key["api-key"] = settings.get_brevo_api_key()
    client = brevo_python.TransactionalEmailsApi(brevo_python.ApiClient(configuration))

    @staticmethod
    def _anonymize_email(email: str) -> str:
        if not email or "@" not in email:
            return email

        local_part, domain = email.split("@", 1)
        if len(local_part) <= 2:
            return email

        anonymized_local = local_part[0] + local_part[1] + "*" * (len(local_part) - 2)
        return f"{anonymized_local}@{domain}"

    @staticmethod
    def send_email(email: Email):
        if len(email.recipients) == 0:
            EmailService.logger.warning("No recipients provided for email, doing nothing")

        sender_info = {"name": email.sender_name, "email": email.sender_email}
        to_field = [{"email": r} for r in email.recipients]

        for recipient in email.recipients:
            email_data = brevo_python.SendSmtpEmail(
                sender=sender_info,
                to=to_field,
                subject=email.subject,
                html_content=email.html_body,
                text_content=email.text_body,
                reply_to={"email": email.reply_to} if email.reply_to else None,
                headers=email.headers or None,
            )

            try:
                EmailService.client.send_transac_email(email_data)
                anonymized_recipient = EmailService._anonymize_email(recipient)
                EmailService.logger.info(f"Email sent successfully to {anonymized_recipient}")
            except ApiException as e:
                EmailService.logger.error(f"Error sending email: {e}")
