import os
import multiprocessing
import logging
import smtplib
from email.mime.text import MIMEText

from app.core.jobs import send_smart_alerts
from app.core.mail.newsletter import get_user_email
from app.core.supabase_client import supabase
from app.core.alerts import create_alert, get_user_alerts, build_embedding

os.environ.update({
    "EMAIL_BACKEND": "local_dev_only_smtp",
    "EMAIL_HOST": "localhost",
    "EMAIL_PORT": "1025",
    "EMAIL_USER": "",
    "EMAIL_PASS": "",
    "EMAIL_USE_TLS": "false",   # or "0"
    "ENVIRONMENT": "development",
})

logging.basicConfig(
    level=logging.INFO,  # or logging.DEBUG for more detail
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

# or wherever your embedding logic lives!

# Set this to the test alert ID you want to update, or loop over all
""" alert_rows = supabase.table("alerts").select("*").execute().data

for alert in alert_rows:
    new_emb = build_embedding(alert['description'])   # ensure you use the same context logic
    supabase.table("alerts").update({"embedding": new_emb}).eq("id", alert["id"]).execute()
    print(f"Updated alert {alert['id']}") """


""" import smtplib
from email.mime.text import MIMEText

msg = MIMEText("Hello from local test!")
msg["Subject"] = "Mailpit Test"
msg["From"] = "sender@example.com"
msg["To"] = "receiver@example.com"

with smtplib.SMTP("localhost", 1025) as server:
    server.send_message(msg) """


USER_EMAIL = "ju-kleinle@web.de"
PROFILE_NAME = "Julius Kleinle"


import smtplib
from email.mime.text import MIMEText


print("=== Starting test_run_smart_alerts.py ===")


msg = MIMEText("Hello from local test!")
msg["Subject"] = "Mailpit Test"
msg["From"] = "sender@example.com"
msg["To"] = "receiver@example.com"

with smtplib.SMTP("localhost", 1025) as server:
    server.send_message(msg)


# Step 1: Create/check user via Admin API
def get_or_create_user(email):
    resp = supabase.auth.admin.list_users()
    users = resp["users"] if isinstance(resp, dict) and "users" in resp else resp
    user = next((u for u in users if getattr(u, "email", None) == email), None)
    if user:
        print("User already exists:", user.id)
        return user.id
    print("Creating test user via Admin API...")
    resp = supabase.auth.admin.create_user({"email": email, "password": "testpassword", "email_confirm": True})
    user_id = resp.user.id if hasattr(resp, "user") else resp["user"]["id"]
    print("Created user:", user_id)
    return user_id


USER_ID = get_or_create_user(USER_EMAIL)


def ensure_profile_exists():
    resp = supabase.table("profiles").select("*").eq("id", USER_ID).execute()
    if not resp.data:
        print("Inserting profile row...")
        supabase.table("profiles").insert(
            {
                "id": USER_ID,
                "name": PROFILE_NAME,
                "surname": "Kleinle",
                "company_name": "TestCompany",
                "company_description": "Test company description",
                "embedding": [0.0] * 1536,
                "newsletter_frequency": "daily",
                "countries": [],  # Required, since 'countries' is not null!
            }
        ).execute()


def ensure_alert_exists():
    alerts = get_user_alerts(USER_ID)
    if not alerts:
        print("Creating dummy alert...")
        create_alert(user_id=USER_ID, description="Test alert for dev")


def test_get_user_email():
    email = get_user_email(USER_ID)
    print("Fetched email:", email)


if __name__ == "__main__":
    ensure_profile_exists()
    test_get_user_email()
    ensure_alert_exists()

    stop_event = multiprocessing.Event()
    print("Running send_smart_alerts...")
    send_smart_alerts(stop_event)


print("=== About to call send_smart_alerts ===")
