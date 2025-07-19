import logging
from datetime import datetime, timezone
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.email import Email, EmailService
from app.core.mail.newsletter import get_user_email, get_user_name, _load_base64_text_file
from app.core.openai_client import openai
from app.core.supabase_client import supabase
from app.core.alerts import mark_alert_ran, set_alert_active

logger = logging.getLogger(__name__)


"""Utilities for composing and sending *smart‑alert* emails.

This mirrors the structure of `app/core/mail/newsletter.py` so future
maintainers can rely on a consistent mental model.
"""


# ================ Subject line generation (GPT) ================
_SUBJECT_PROMPT_TMPL = (
    "You are an email subject generator for EU startup founders. "
    "Create a catchy subject line (max 8 words) that summarises the alert and "
    "the first three meeting titles. Avoid emojis.\n\n"
    "Alert: {alert}\n"
    "Meetings: {titles}"
)


def _generate_subject(alert: dict, meetings: list[dict]) -> str:
    """Return a catchy subject line via GPT; fall back to static if error."""
    meeting_titles = ", ".join(m["title"] for m in meetings[:3])
    prompt = _SUBJECT_PROMPT_TMPL.format(alert=alert["description"], titles=meeting_titles)

    try:
        resp = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as exc:  # pylint: disable=broad-except
        logger.error("GPT subject generation failed – %s; falling back", exc)
        # graceful degradation
        return f"New meetings for your alert – {datetime.now().date()}"


# ================ Email body rendering ================
_BASE_DIR = Path(__file__).parent
_LOGO_PATH = _BASE_DIR / "logo1.b64"  # reuse the same logo asset as newsletter
_TEMPLATE_NAME = "alert_mailbody.html.j2"


def _build_email_body(*, alert: dict, meetings: list[dict], user_id: str) -> tuple[str, float]:
    """Render the HTML body for an alert email and return (html, mean_similarity)."""
    if not _LOGO_PATH.exists():
        raise FileNotFoundError(f"Expected Base64 logo file not found: {_LOGO_PATH}")

    logo_b64 = _load_base64_text_file(_LOGO_PATH)

    template_path = _BASE_DIR / _TEMPLATE_NAME
    if not template_path.exists():
        raise FileNotFoundError(f"Email template not found: {template_path}")

    env = Environment(
        loader=FileSystemLoader(str(_BASE_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template(_TEMPLATE_NAME)

    # Compute mean similarity for analytics / notifications
    similarities = [m.get("similarity", 0.0) for m in meetings]
    mean_similarity = sum(similarities) / len(similarities) if similarities else 0.0

    context = {
        "alert": alert,
        "meetings": meetings,
        "image1_base64": logo_b64,
        "current_year": datetime.now().year,
        "recipient": get_user_name(user_id),
    }

    rendered_html = template.render(**context)
    return rendered_html, mean_similarity


# ================ Public mailer facade ================
class SmartAlertMailer:
    email_client = EmailService()

    @staticmethod
    def send_alert_email(*, user_id: str, alert: dict, meetings: list[dict]):
        user_mail = get_user_email(user_id=user_id)
        if not user_mail:
            logger.warning("No email address for user_id=%s; skipping alert email", user_id)
            return False  # <--- Indicate no email sent

        subject = _generate_subject(alert, meetings)
        mail_body, mean_sim = _build_email_body(alert=alert, meetings=meetings, user_id=user_id)

        mail = Email(subject=subject, html_body=mail_body, recipients=[user_mail])
        try:
            SmartAlertMailer.email_client.send_email(mail)
            logger.info("Smart alert email sent to user_id=%s (alert=%s)", user_id, alert["id"])
            # Write to notifications table instead of alert_notifications
            max_similarity = max((m.get("similarity", 0.0) for m in meetings), default=None)
            supabase.table("notifications").insert(
                {
                    "user_id": alert["user_id"],
                    "sent_at": datetime.now(timezone.utc).isoformat(),
                    "type": "smart_alert",
                    "message": mail_body,  # Save the HTML email here
                    "relevance_score": max_similarity,
                    "message_subject": subject,
                }
            ).execute()
            mark_alert_ran(alert["id"])
            set_alert_active(alert["id"], active=False)
            return True  # <--- Success!
        except Exception as exc:
            logger.error("Failed to send smart alert to user_id=%s: %s", user_id, exc)
            return False
