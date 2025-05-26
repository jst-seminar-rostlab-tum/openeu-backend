import logging

import brevo_python
from brevo_python.rest import ApiException

from app.core.config import Settings


class Email:
    def __init__(self, subject: str, html_body: str, recipients: list[str]):
        self.subject = subject
        self.html_body = html_body
        self.recipients = recipients


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
    def _anonymize_email_list(emails: list[str]) -> str:
        anonymized = [EmailService._anonymize_email(email) for email in emails]
        return ", ".join(anonymized)

    @staticmethod
    def send_email(email: Email):
        sender = {"name": "OpenEU", "email": "mail@openeu.csee.tech"}
        to = [{"email": recipient} for recipient in email.recipients]
        email_data = brevo_python.SendSmtpEmail(
            to=to,
            html_content=email.html_body,
            sender=sender,
            subject=email.subject,
        )

        try:
            EmailService.client.send_transac_email(email_data)
            anonymized_recipients = EmailService._anonymize_email_list(email.recipients)
            EmailService.logger.info(f"Email sent successfully to {anonymized_recipients}")
        except ApiException as e:
            EmailService.logger.error(f"Error sending email: {e}")
