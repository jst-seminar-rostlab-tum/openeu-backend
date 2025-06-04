from pathlib import Path
from datetime import datetime
from typing import Optional
from app.core.supabase_client import supabase
from app.core.relevant_meetings import fetch_relevant_meetings
from app.core.email import Email, EmailService
import logging

from jinja2 import Environment, FileSystemLoader, select_autoescape

    
    
def get_user_email(user_id: str) -> Optional[str]:
    """
    Fetches the email address of a user from the auth.users table using a SQL function.
    
    Args:
        user_id (str): The UUID of the user.

    Returns:
        str | None: The email of the user if found, else None.
    """
    response = supabase.rpc("get_user_by_id", {"uid": user_id}).execute()
        
    if response.data and len(response.data) > 0:
        return response.data
    else:
        print("User not found.")
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

    except Exception as e:
        return ""




def build_email_for_user(user_id: str) -> str:
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
    # Determine the directory where this script lives
    
    base_dir = Path(__file__).parent
    
    # 1. Fetch meetings and validate via Pydantic
    response_obj = fetch_relevant_meetings(user_id=user_id, k=10)
    
    name_of_recipient = get_user_name(user_id=user_id)
    
    
    image1_path = base_dir / "logo1.b64"

    if not image1_path.exists():
        raise FileNotFoundError(f"Expected Base64 file not found: {image1_path}")
   

    image1_b64 = _load_base64_text_file(image1_path)

    # 3. Prepare Jinja2 environment and load the mail.html.j2 template
    template_path = base_dir / "newsletter_mailbody.html.j2"
    
    if not template_path.exists():
        raise FileNotFoundError(f"Email template not found: {template_path}")

    env = Environment(
        loader=FileSystemLoader(str(base_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    
    template = env.get_template("newsletter_mailbody.html.j2")

    # 4. Build the context for rendering
    context = {
        "meetings": response_obj.meetings,
        "image1_base64": image1_b64,
        "current_year": datetime.now().year,
        "recipient": name_of_recipient
    }

    # 5. Render and return the HTML string
    rendered_html = template.render(**context)
    return rendered_html


class Newsletter():
    email_client = EmailService()
    logger = logging.getLogger(__name__)

    
    @staticmethod
    def send_newsletter_to_user(user_id):
        user_mail = get_user_email(user_id=user_id)
        mail_body = build_email_for_user(user_id=user_id)
        
        mail = Email(
            subject="OpenEU Meeting Newsletter", html_body=mail_body, recipients=[user_mail]
        )
        try:
            Newsletter.email_client.send_email(mail)
            EmailService.logger(f"Newsletter send succesfully to user_id={user_id}")
        except:
            EmailService.logger(f"Failed to send newsletter for user_id={user_id}")
            
            
        notification_payload = {
                "user_id": user_id,
                "type": "newsletter",
                "message": f"Sent email: {mail.subject}"
        }
        supabase.table("notifications").insert(notification_payload).execute()



Newsletter().send_newsletter_to_user("456378e1-39f2-4715-98d9-78f80698ffb0")