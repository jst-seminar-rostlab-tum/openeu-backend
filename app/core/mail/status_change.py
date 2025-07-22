import logging
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.email import Email, EmailService
from app.core.supabase_client import supabase
from app.core.mail.newsletter import get_user_email, _load_base64_text_file, get_user_name

logger = logging.getLogger(__name__)
email_client = EmailService()

_TEMPLATE_NAME = "status_change_mailbody.html.j2"
_BASE_DIR = Path(__file__).parent
_LOGO_PATH = _BASE_DIR / "logo1.b64"

def build_email_body(user_id: str, legislation: dict, old_status: str) -> str:
    """Render HTML for status change email."""
    template_path = _BASE_DIR / _TEMPLATE_NAME
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    env = Environment(loader=FileSystemLoader(str(_BASE_DIR)), autoescape=select_autoescape(["html", "xml"]))
    template = env.get_template(_TEMPLATE_NAME)

    context = {
        "recipient": get_user_name(user_id),
        "title": legislation.get("title"),
        "link": legislation.get("details_link") or legislation.get("link"),
        "old_status": old_status,
        "new_status": legislation.get("status"),
        "current_year": datetime.now().year,
        "logo_base64": _load_base64_text_file(_LOGO_PATH),
    }

    return template.render(**context)


def notify_status_change(user_id: str, legislation: dict, old_status: str) -> bool:
    user_email = get_user_email(user_id)
    if not user_email:
        logger.warning(f"No email found for user {user_id}; skipping")
        return False

    subject = f"Status update on legislation: {legislation.get('id') or 'Unknown'}"
    html_body = build_email_body(user_id, legislation, old_status)

    msg = Email(subject=subject, html_body=html_body, recipients=[user_email])
    try:
        email_client.send_email(msg)
        logger.info(f"Status change email sent to {user_id} for {legislation.get('id')}")
        supabase.table("notifications").insert(
            {
                "user_id": user_id,
                "type": "status_change",
                "message": html_body,
                "message_subject": subject,
                "relevance_score": None,
                "sent_at": datetime.utcnow().isoformat(),
            }
        ).execute()
        return True
    except Exception as e:
        logger.error(f"Failed to send status change email: {e}")
        return False
