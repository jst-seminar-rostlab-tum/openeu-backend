import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.email import Email, EmailService
from app.core.relevant_meetings import RelevantMeetingsResponse, fetch_relevant_meetings
from app.core.supabase_client import supabase

logger = logging.getLogger(__name__)


def get_user_email(user_id: str) -> Optional[str]:
    """
    Fetches the email address of a user from the auth.users table using a SQL function.

    Args:
        user_id (str): The UUID of the user.

    Returns:
        str | None: The email of the user if found, else None.
    """

    try:
        response = supabase.auth.admin.get_user_by_id(user_id)
    except Exception as e:
        logger.error(f"Error calling get_user_by_id for user_id={user_id}: {e}")
        return None

    user_mail = response.user.email

    if user_mail:
        return user_mail

    else:
        logger.info(f"User not found or has no email: user_id={user_id}")
        return None


def _load_base64_text_file(path: Path) -> str:
    """
    Reads a file containing raw Base64 data (no "data:image/..." header)
    and returns it as one contiguous string.
    """
    content = path.read_text(encoding="utf-8").strip().replace("\n", "")
    return content


def get_user_name(user_id: str) -> Optional[str]:
    """
    Fetches the name of a user from the profiles table.

    Args:
        user_id (str): The UUID of the user.

    Returns:
        str | None: The name of the user if found, else None.
    """
    try:
        response = supabase.table("profiles").select("name").eq("id", user_id).single().execute()

        if response.data:
            return response.data["name"]
        else:
            return ""

    except Exception:
        return ""


def build_email_for_user(user_id: str, meetings_response: RelevantMeetingsResponse) -> tuple[str, float]:
    """
    Renders and returns an HTML email (as a string) for the given user_id.
    This function will:
      1. Fetch relevant meetings for that user via get_relevant_meetings_for_user().
      2. Wrap them into a RelevantMeetingsResponse.
      3. Load two Base64‐encoded image files (image1.b64, image2.b64) from the same directory.
      4. Load the Jinja2 template mail.html.j2 from the same directory.
      5. Render the template with all context variables (meetings, images, current year).
      6. Return the rendered HTML as a string.
    """

    base_dir = Path(__file__).parent

    name_of_recipient = get_user_name(user_id=user_id)

    image1_path = base_dir / "logo1.b64"

    if not image1_path.exists():
        raise FileNotFoundError(f"Expected Base64 file not found: {image1_path}")

    image1_b64 = _load_base64_text_file(image1_path)

    template_path = base_dir / "newsletter_mailbody.html.j2"

    if not template_path.exists():
        raise FileNotFoundError(f"Email template not found: {template_path}")

    env = Environment(
        loader=FileSystemLoader(str(base_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )

    template = env.get_template("newsletter_mailbody.html.j2")

    similarities = [m.similarity for m in meetings_response.meetings if m.similarity is not None]
    mean_similarity = sum(similarities) / len(similarities) if similarities else 0.0

    context = {
        "meetings": meetings_response.meetings,
        "image1_base64": image1_b64,
        "current_year": datetime.now().year,
        "recipient": name_of_recipient,
    }

    rendered_html = template.render(**context)
    return rendered_html, mean_similarity


class Newsletter:
    email_client = EmailService()

    @staticmethod
    def send_newsletter_to_user(user_id, frequency: str):
        user_mail = get_user_email(user_id=user_id)
        meetings_response = fetch_relevant_meetings(user_id=user_id, k=10)

        if len(meetings_response.meetings) == 0:
            logger.info(f"No relevant meetings found for user_id={user_id}. No newsletter sent.")
            return

        mail_body, mean_sim = build_email_for_user(user_id=user_id, meetings_response=meetings_response)

        # Adjust subject based on frequency
        subject = "OpenEU Weekly Newsletter" if frequency.lower() == "weekly" else "OpenEU Daily Newsletter"

        if user_mail is not None:
            mail = Email(
                subject=subject + " - " + str(datetime.now().date()),
                html_body=mail_body,
                recipients=[user_mail],
            )
            try:
                logger.info(f"Attempting to send {frequency} email to {user_mail}...")
                Newsletter.email_client.send_email(mail)
                logger.info(f"{frequency.capitalize()} newsletter sent successfully to user_id={user_id}")
            except Exception as e:
                logger.error(f"Failed to send {frequency} newsletter for user_id={user_id}: {e}")

            notification_payload = {
                "user_id": user_id,
                "type": "newsletter",
                "message": str(mail_body),
                "relevance_score": mean_sim,
                "message_subject": subject,
            }
            supabase.table("notifications").insert(notification_payload).execute()
