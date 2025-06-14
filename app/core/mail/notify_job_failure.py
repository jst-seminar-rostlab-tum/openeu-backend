from datetime import datetime, timezone

from app.core.email import Email, EmailService

GITHUB_URL = "https://github.com/jst-seminar-rostlab-tum/openeu-backend"
RENDER_LOG_URL = "https://dashboard.render.com/web/srv-d0vdf7vfte5s739i276g/logs"


def notify_job_failure(job_name: str, error: Exception) -> None:
    """
    Build a transactional e-mail and send it via EmailService.

    Keeps the template in one place so ScheduledJob doesn’t need to
    know how alerting works.
    """
    recipients = ["dogayasa@gmail.com", "trungnguyenb0k30@gmail.com", "bohdan.garchu@tum.de", "nils.jansen@tum.de"]
    reply_to = "trungnguyenb0k30@gmail.com"

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    subject = f"[Heads-up] {job_name} failed at {timestamp}"
    preheader = "No panicking: links inside to GitHub and Render logs."

    # --- Plain-text part -------------------------------------------------
    text_body = f"""
Hello team 👋,

Our scheduled job “{job_name}” just tripped over its own shoelaces.
Error details ↓

{error}

Useful shortcuts:
• GitHub repo : {GITHUB_URL}
• Render logs : {RENDER_LOG_URL}

Grab a ☕, have a quick look, and give the job a gentle reboot
when you’ve finished laughing at the stack trace. 😉

— Your friendly ETL Bot
––––––––––––––––––––––––––––––––––––––––––––––––––––––––
You’re receiving this because you subscribe to job-status alerts.
OpenEU GmbH · Arcisstr. 21 · 80333 Munich · Germany
"""

    # --- HTML part -------------------------------------------------------
    html_body = f"""\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{subject}</title>
  <style>
    body {{font-family:Arial,Helvetica,sans-serif;line-height:1.5;margin:0 1rem;color:#212529;}}
    pre  {{background:#f8f9fa;border:1px solid #e9ecef;padding:12px;border-radius:4px;overflow-x:auto;}}
    a    {{color:#0d6efd;text-decoration:none;}}
    a:hover {{text-decoration:underline;}}
    small{{color:#6c757d;font-size:0.85em;}}
  </style>
</head>
<body>
  <p>👋 Hey team,</p>

  <p>Our scheduled job <strong>{job_name}</strong> just
     <em>stumbled</em> and face-planted.</p>

  <p><strong>Error details:</strong></p>
  <pre>{error}</pre>

  <p><strong>Useful shortcuts:</strong></p>
  <ul>
    <li><a href="{GITHUB_URL}">GitHub repo</a> – poke the code</li>
    <li><a href="{RENDER_LOG_URL}">Render logs</a> – watch the crash in 4K</li>
  </ul>

  <p>Grab a ☕, have a quick look, and give the job a gentle reboot when you’re
     done chuckling at the stack trace. 😉</p>

  <small>
    You’re receiving this because you subscribe to job-status alerts.<br>
    Example&nbsp;GmbH · Arcisstr.&nbsp;21 · 80333&nbsp;Munich · Germany
  </small>
</body>
</html>
"""

    msg = Email(
        subject=subject,
        html_body=html_body,
        text_body=text_body,
        recipients=recipients,
        reply_to=reply_to,
        headers={"X-Preheader": preheader},
    )

    EmailService.send_email(msg)
