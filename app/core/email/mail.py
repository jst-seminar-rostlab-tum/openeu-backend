import os

from jinja2 import Environment, FileSystemLoader

from app.core.email import Email, EmailService
from app.core.relevant_meetings import fetch_relevant_meetings
from app.core.supabase_client import supabase
from app.models.meeting import RelevantMeetingsResponse


def format_meetings(response: RelevantMeetingsResponse):
    return [
        {
            "title": meeting.title,
            "date": meeting.meeting_start_datetime.isoformat(),
            "description": meeting.description or "",
        }
        for meeting in response.meetings
    ]


def send_meetings_newsletter(user_id: str):
    env = Environment(
        loader=FileSystemLoader(os.getcwd() + "/app/core/email/"),
        autoescape=True,
    )
    try:
        resp = supabase.table("auth.users").select("email").eq("id", user_id).single().execute()
        email = resp.data["email"]

    except Exception:
        raise

    meetings = format_meetings(fetch_relevant_meetings(user_id=user_id, k=10))

    template = env.get_template("mailbody.html.j2")

    html_body = template.render(meetings=meetings)

    email_to_send = Email(recipients=[email], subject="Upcoming Meetings", html_body=html_body)

    EmailService.send_email(email=email_to_send)
