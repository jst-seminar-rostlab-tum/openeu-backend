import os
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pydantic import BaseModel

# ----------------------------------------------------------------------
# Pydantic models (reproduce or import from your existing codebase)
# ----------------------------------------------------------------------
class Meeting(BaseModel):
    meeting_id: str
    title: str
    status: Optional[str] = None
    meeting_url: Optional[str] = None
    meeting_start_datetime: datetime
    meeting_end_datetime: Optional[datetime] = None
    location: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    similarity: Optional[float] = None


class RelevantMeetingsResponse(BaseModel):
    meetings: List[Meeting]


# ----------------------------------------------------------------------
# Placeholder: replace this with your actual function that fetches meetings.
# It should return a list of dicts or Meeting instances for the given user_id.
# ----------------------------------------------------------------------
def get_relevant_meetings_for_user(user_id: str) -> List[Meeting]:
    """
    This is a stub. Replace its implementation with your actual data-fetching logic.
    Example return value (as dicts) could be:
        [
            {
                "meeting_id": "abc123",
                "title": "Quarterly Review",
                "status": "Confirmed",
                "meeting_url": "https://example.com/meet/abc123",
                "meeting_start_datetime": "2025-06-10T14:00:00",
                "meeting_end_datetime": "2025-06-10T15:00:00",
                "location": "Conference Room A",
                "description": "Discuss Q2 performance",
                "tags": ["Finance", "Q2"],
                "similarity": 0.87
            },
            # … more meetings …
        ]
    """
    # Example stub: return an empty list for demonstration
    return [
            {
                "meeting_id": "abc123",
                "title": "Quarterly Review",
                "status": "Confirmed",
                "meeting_url": "https://example.com/meet/abc123",
                "meeting_start_datetime": "2025-06-10T14:00:00",
                "meeting_end_datetime": "2025-06-10T15:00:00",
                "location": "Conference Room A",
                "description": "Discuss Q2 performance",
                "tags": ["Finance", "Q2"],
                "similarity": 0.87
            }
        ]


# ----------------------------------------------------------------------
# Helper to load a small Base64 file (no header lines) into a single string
# ----------------------------------------------------------------------
def _load_base64_text_file(path: Path) -> str:
    """
    Reads a file containing raw Base64 data (no "data:image/..." header)
    and returns it as one contiguous string.
    """
    content = path.read_text(encoding="utf-8").strip().replace("\n", "")
    return content


# ----------------------------------------------------------------------
# Main function: build the email HTML for a given user_id
# ----------------------------------------------------------------------
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

    Assumptions:
      • The two Base64 files are named "image1.b64" and "image2.b64".
      • The Jinja2 template is named "mail.html.j2".
      • All three files live in the same folder as this script.
      • get_relevant_meetings_for_user() returns a List[Meeting] or a list of dicts
        that can be parsed by the Meeting model.
    """
    # Determine the directory where this script lives
    base_dir = Path(__file__).parent

    # 1. Fetch meetings and validate via Pydantic
    raw_meetings = get_relevant_meetings_for_user(user_id)
    # If raw_meetings are dicts, we can do:
    response_obj = RelevantMeetingsResponse(meetings=raw_meetings)

    # 2. Load Base64 images
    image1_path = base_dir / "logo1.b64"
    image2_path = base_dir / "logo2.b64"

    if not image1_path.exists():
        raise FileNotFoundError(f"Expected Base64 file not found: {image1_path}")
    if not image2_path.exists():
        raise FileNotFoundError(f"Expected Base64 file not found: {image2_path}")

    image1_b64 = _load_base64_text_file(image1_path)
    image2_b64 = _load_base64_text_file(image2_path)

    # 3. Prepare Jinja2 environment and load the mail.html.j2 template
    template_path = base_dir / "mailbody.html.j2"
    if not template_path.exists():
        raise FileNotFoundError(f"Email template not found: {template_path}")

    env = Environment(
        loader=FileSystemLoader(str(base_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("mailbody.html.j2")

    # 4. Build the context for rendering
    context = {
        "meetings": response_obj.meetings,
        "image1_base64": image1_b64,
        "current_year": datetime.now().year,
    }

    # 5. Render and return the HTML string
    rendered_html = template.render(**context)
    return rendered_html


# ----------------------------------------------------------------------
# Example usage (uncomment to test)
# ----------------------------------------------------------------------
user_id = "user_123"
html_content = build_email_for_user(user_id)
with open("output_email.html", "w", encoding="utf-8") as f:
    f.write(html_content)
print("Generated output_email.html")
