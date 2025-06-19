import logging
from datetime import datetime

import schedule

from app.core.extract_topics import TopicExtractor
from app.core.mail.newsletter import Newsletter
from app.core.scheduling import scheduler
from app.core.supabase_client import supabase
from app.data_sources.apis.austrian_parliament import run_scraper
from app.data_sources.apis.mep import fetch_and_store_current_meps
from app.data_sources.scrapers.belgian_parliament_scraper import run_scraper as run_belgian_parliament_scraper
from app.data_sources.scrapers.bundestag_drucksachen_scraper import BundestagDrucksachenScraper
from app.data_sources.scrapers.bundestag_plenarprotocol_scaper import BundestagPlenarprotokolleScraper
from app.data_sources.scrapers.ipex_calender_scraper import run_scraper as run_ipex_calendar_scraper
from app.data_sources.scrapers.lawtracker_topic_scraper import LawTrackerSpider
from app.data_sources.scrapers.legislative_observatory_scraper import LegislativeObservatoryScraper
from app.data_sources.scrapers.mec_prep_bodies_meetings_scraper import MECPrepBodiesMeetingsScraper
from app.data_sources.scrapers.mec_sum_minist_meetings_scraper import MECSumMinistMeetingsScraper
from app.data_sources.scrapers.meeting_calendar_scraper import EPMeetingCalendarScraper
from app.data_sources.scrapers.mep_meetings_scraper import MEPMeetingsScraper
from app.data_sources.scrapers.polish_presidency_meetings_scraper import PolishPresidencyMeetingsScraper
from app.data_sources.scrapers.spanish_commission_scraper import SpanishCommissionScraper
from app.data_sources.scrapers.tweets import TweetScraper
from app.data_sources.scrapers.weekly_agenda_scraper import WeeklyAgendaScraper
from scripts.embedding_cleanup import embedding_cleanup

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


def _send_newsletter(frequency: str):
    daily_newsletter_subscribers = (
        supabase.table("profiles").select("id").eq("newsletter_frequency", frequency).execute()
    )
    user_ids = [user["id"] for user in daily_newsletter_subscribers.data] if daily_newsletter_subscribers.data else []

    logger.info(f"Sending {frequency} newsletter to {len(user_ids)} users")

    for user_id in user_ids:
        Newsletter.send_newsletter_to_user(user_id)


def send_daily_newsletter():
    return _send_newsletter("daily")


def send_weekly_newsletter():
    return _send_newsletter("weekly")


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


def scrape_tweets():
    usernames = ["EU_Commission", "EUCouncil", "epc_eu", "Euractiv"]
    scraper = TweetScraper(usernames=usernames)
    return scraper.scrape()


def scrape_legislative_observatory():
    scraper = LegislativeObservatoryScraper()
    return scraper.scrape()


def clean_up_embeddings():
    embedding_cleanup()


def extract_topics_from_meetings():
    extractor = TopicExtractor()
    extractor.extract_topics_from_meetings(n_clusters=15, top_n_keywords=20)


def setup_scheduled_jobs():
    scheduler.register(
        "fetch_and_store_current_meps", fetch_and_store_current_meps, schedule.every().monday.at("02:00")
    )
    scheduler.register(
        "scrape_meeting_calendar_for_current_day",
        scrape_meeting_calendar_for_current_day,
        schedule.every().day.at("02:10"),
    )
    scheduler.register(
        "scrape_mep_meetings", scrape_mep_meetings, schedule.every().day.at("02:20"), run_in_process=True
    )
    scheduler.register("scrape_ipex_calendar", scrape_ipex_calendar, schedule.every().day.at("02:30"))
    scheduler.register(
        "scrape_mec_sum_minist_meetings", scrape_mec_sum_minist_meetings, schedule.every().day.at("02:40")
    )
    scheduler.register(
        "scrape_mec_prep_bodies_meetings", scrape_mec_prep_bodies_meetings, schedule.every().day.at("02:50")
    )
    scheduler.register(
        "scrape_weekly_agenda", scrape_weekly_agenda, schedule.every().monday.at("03:00"), run_in_process=True
    )
    scheduler.register(
        "scrape_belgian_parliament_meetings", scrape_belgian_parliament_meetings, schedule.every().day.at("03:10")
    )
    scheduler.register(
        "scrape_austrian_parliament_meetings",
        scrape_austrian_parliament_meetings,
        schedule.every().day.at("03:20"),
    )
    scheduler.register(
        "scrape_polish_presidency_meetings",
        scrape_polish_presidency_meetings,
        schedule.every().day.at("03:40"),
        run_in_process=True,
    )
    scheduler.register(
        "scrape_spanish_commission_meetings",
        scrape_spanish_commission_meetings,
        schedule.every().day.at("03:50"),
        run_in_process=True,
    )
    scheduler.register("scrape_bundestag_drucksachen", scrape_bundestag_drucksachen, schedule.every().day.at("04:00"))
    scheduler.register(
        "scrape_bundestag_plenary_protocols", scrape_bundestag_plenary_protocols, schedule.every().day.at("04:10")
    )
    scheduler.register(
        "scrape_legislative_observatory",
        scrape_legislative_observatory,
        schedule.every().day.at("04:20"),
        run_in_process=True,
    )
    scheduler.register("send_daily_newsletter", send_daily_newsletter, schedule.every().day.at("08:00"))
    scheduler.register("send_weekly_newsletter", send_weekly_newsletter, schedule.every().monday.at("08:00"))
    scheduler.register("clean_up_embeddings", clean_up_embeddings, schedule.every().day.at("04:40"))
    scheduler.register("scrape_tweets", scrape_tweets, schedule.every().day.at("04:50"))
    scheduler.register(
        "extract_topics_from_meetings", extract_topics_from_meetings, schedule.every().monday.at("05:00")
    )
