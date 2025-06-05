import logging
from datetime import datetime

from app.core.email import Email, EmailService
from app.core.scheduling import scheduler
from app.core.supabase_client import supabase
from app.data_sources.apis.austrian_parliament import run_scraper
from app.data_sources.apis.mep import fetch_and_store_current_meps
from app.data_sources.scrapers.belgian_parliament_scraper import run_scraper as run_belgian_parliament_scraper
from app.data_sources.scrapers.bundestag_drucksachen_scraper import BundestagDrucksachenScraper
from app.data_sources.scrapers.bundestag_plenarprotocol_scaper import BundestagPlenarprotokolleScraper
from app.data_sources.scrapers.ipex_calender_scraper import run_scraper as run_ipex_calendar_scraper
from app.data_sources.scrapers.lawtracker_topic_scraper import LawTrackerSpider
from app.data_sources.scrapers.mec_prep_bodies_meetings_scraper import MECPrepBodiesMeetingsScraper
from app.data_sources.scrapers.mec_sum_minist_meetings_scraper import MECSumMinistMeetingsScraper
from app.data_sources.scrapers.meeting_calendar_scraper import EPMeetingCalendarScraper
from app.data_sources.scrapers.mep_meetings_scraper import MEPMeetingsScraper
from app.data_sources.scrapers.polish_presidency_meetings_scraper import PolishPresidencyMeetingsScraper
from app.data_sources.scrapers.spanish_commission_scraper import SpanishCommissionScraper
from app.data_sources.scrapers.weekly_agenda_scraper import WeeklyAgendaScraper
from scripts.embedding_cleanup import embedding_cleanup

DAILY_INTERVAL_MINUTES = 24 * 60
WEEKLY_INTERVAL_MINUTES = 7 * DAILY_INTERVAL_MINUTES

logger = logging.getLogger(__name__)


def scrape_eu_laws_by_topic():
    lawtracker = LawTrackerSpider()
    return lawtracker.scrape()


def scrape_ipex_calendar():
    today = datetime.now().date()
    return run_ipex_calendar_scraper(start_date=today, end_date=today)


def scrape_meeting_calendar_for_current_day():
    now = datetime.now()
    ep_meeting_scraper = EPMeetingCalendarScraper(now, now)
    return ep_meeting_scraper.scrape()


def scrape_mep_meetings():
    today = datetime.now().date()
    scraper = MEPMeetingsScraper(start_date=today, end_date=today)
    return scraper.scrape()


def scrape_mec_sum_minist_meetings():
    today = datetime.now().date()
    scraper = MECSumMinistMeetingsScraper(start_date=today, end_date=today)
    return scraper.scrape()


def scrape_belgian_parliament_meetings():
    today = datetime.now().date()
    return run_belgian_parliament_scraper(start_date=today, end_date=today)


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


def scrape_mec_prep_bodies_meetings():
    today = datetime.now().date()
    scraper = MECPrepBodiesMeetingsScraper(start_date=today, end_date=today)
    return scraper.scrape()


def scrape_weekly_agenda():
    today = datetime.now().date()
    scraper = WeeklyAgendaScraper(start_date=today, end_date=today)
    return scraper.scrape()


def scrape_austrian_parliament_meetings():
    today = datetime.now().date()
    return run_scraper(start_date=today, end_date=today)


def scrape_polish_presidency_meetings():
    today = datetime.now().date()
    scraper = PolishPresidencyMeetingsScraper(start_date=today, end_date=today)
    return scraper.scrape()


def scrape_spanish_commission_meetings():
    today = datetime.now().date()
    scraper = SpanishCommissionScraper(date=today)
    return scraper.scrape()


def scrape_bundestag_plenary_protocols():
    today = datetime.now().date()
    scraper = BundestagPlenarprotokolleScraper()
    scraper.scrape(start_date=today, end_date=today)


def scrape_bundestag_drucksachen():
    today = datetime.now().date()
    scraper = BundestagDrucksachenScraper()
    scraper.scrape(start_date=today, end_date=today)


def clean_up_embeddings():
    embedding_cleanup()


def setup_scheduled_jobs():
    scheduler.register("fetch_and_store_current_meps", fetch_and_store_current_meps, WEEKLY_INTERVAL_MINUTES)
    scheduler.register("scrape_eu_laws_by_topic", scrape_eu_laws_by_topic, WEEKLY_INTERVAL_MINUTES)
    scheduler.register(
        "scrape_meeting_calendar_for_current_day", scrape_meeting_calendar_for_current_day, DAILY_INTERVAL_MINUTES
    )
    scheduler.register("scrape_mep_meetings", scrape_mep_meetings, DAILY_INTERVAL_MINUTES, use_process=True)
    scheduler.register("scrape_ipex_calendar", scrape_ipex_calendar, DAILY_INTERVAL_MINUTES)
    scheduler.register("scrape_mec_sum_minist_meetings", scrape_mec_sum_minist_meetings, DAILY_INTERVAL_MINUTES)
    scheduler.register("scrape_mec_prep_bodies_meetings", scrape_mec_prep_bodies_meetings, DAILY_INTERVAL_MINUTES)
    scheduler.register("scrape_weekly_agenda", scrape_weekly_agenda, WEEKLY_INTERVAL_MINUTES)
    scheduler.register("scrape_belgian_parliament_meetings", scrape_belgian_parliament_meetings, DAILY_INTERVAL_MINUTES)
    scheduler.register(
        "scrape_austrian_parliament_meetings", scrape_austrian_parliament_meetings, DAILY_INTERVAL_MINUTES
    )
    scheduler.register("scrape_polish_presidency_meetings", scrape_polish_presidency_meetings, DAILY_INTERVAL_MINUTES)
    scheduler.register("scrape_spanish_commission_meetings", scrape_spanish_commission_meetings, DAILY_INTERVAL_MINUTES)
    scheduler.register("scrape_bundestag_drucksachen", scrape_bundestag_drucksachen, DAILY_INTERVAL_MINUTES)
    scheduler.register("scrape_bundestag_plenary_protocols", scrape_bundestag_plenary_protocols, DAILY_INTERVAL_MINUTES)

    scheduler.register("send_daily_newsletter", send_daily_newsletter, DAILY_INTERVAL_MINUTES)
    scheduler.register("clean_up_embeddings", clean_up_embeddings, DAILY_INTERVAL_MINUTES)
