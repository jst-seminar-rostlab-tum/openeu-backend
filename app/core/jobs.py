import logging
from datetime import datetime

from app.core.email import Email, EmailService
from app.core.scheduling import scheduler
from app.core.supabase_client import supabase
from app.data_sources.apis.mep import fetch_and_store_current_meps
from app.data_sources.scrapers.ipex_calender_scraper import IPEXCalendarAPIScraper
from app.data_sources.scrapers.mec_sum_minist_meetings_scraper import MECSumMinistMeetingsScraper
from app.data_sources.scrapers.meeting_calendar_scraper import scrape_meeting_calendar
from app.data_sources.scrapers.mep_meetings_scraper import scrape_and_store_meetings

DAILY_INTERVAL_MINUTES = 24 * 60
WEEKLY_INTERVAL_MINUTES = 7 * DAILY_INTERVAL_MINUTES

logger = logging.getLogger(__name__)


def scrape_ipex_calendar():
    ipex_scraper = IPEXCalendarAPIScraper()
    ipex_scraper.scrape()


def scrape_meeting_calendar_for_current_day():
    now = datetime.now()
    now_str = now.strftime("%d-%m-%Y")
    scrape_meeting_calendar(now_str, now_str)


def scrape_mep_meetings():
    today = datetime.now().date()
    scrape_and_store_meetings(today, today)


def scrape_mec_sum_minist_meetings():
    today = datetime.now().date()
    scraper = MECSumMinistMeetingsScraper(start_date=today, end_date=today)
    scraper.scrape(today, today)


def send_daily_newsletter():
    users = supabase.auth.admin.list_users()
    email_addresses = [user.email for user in users]
    email_message = Email(
        subject="OpenEU Daily Newsletter",
        html_body="<p>Here is your daily newsletter from OpenEU.</p>",
        recipients=email_addresses,
    )
    logger.info(f"Sending daily newsletter to {len(email_addresses)} users")
    EmailService.send_email(email=email_message)


def setup_scheduled_jobs():
    scheduler.register("fetch_and_store_current_meps", fetch_and_store_current_meps, WEEKLY_INTERVAL_MINUTES)
    scheduler.register(
        "scrape_meeting_calendar_for_current_day", scrape_meeting_calendar_for_current_day, DAILY_INTERVAL_MINUTES
    )
    scheduler.register("scrape_mep_meetings", scrape_mep_meetings, DAILY_INTERVAL_MINUTES)
    scheduler.register("scrape_ipex_calendar", scrape_ipex_calendar, DAILY_INTERVAL_MINUTES)
    scheduler.register("scrape_mec_sum_minist_meetings", scrape_mec_sum_minist_meetings, DAILY_INTERVAL_MINUTES)
    scheduler.register("send_daily_newsletter", send_daily_newsletter, DAILY_INTERVAL_MINUTES)
