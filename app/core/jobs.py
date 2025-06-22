import logging
import multiprocessing
from datetime import datetime, timedelta

import schedule

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


def scrape_eu_laws_by_topic(stop_event: multiprocessing.synchronize.Event):
    lawtracker = LawTrackerSpider(stop_event=stop_event)
    return lawtracker.scrape()


def scrape_ipex_calendar(stop_event: multiprocessing.synchronize.Event):
    today = datetime.now().date()
    return run_ipex_calendar_scraper(start_date=today, end_date=today, stop_event=stop_event)


def scrape_meeting_calendar_for_current_day(stop_event: multiprocessing.synchronize.Event):
    now = datetime.now()
    ep_meeting_scraper = EPMeetingCalendarScraper(now, now, stop_event=stop_event)
    return ep_meeting_scraper.scrape()


def scrape_mep_meetings(stop_event: multiprocessing.synchronize.Event):
    today = datetime.now().date()
    scraper = MEPMeetingsScraper(start_date=today, end_date=today, stop_event=stop_event)
    return scraper.scrape()


def scrape_mec_sum_minist_meetings(stop_event: multiprocessing.synchronize.Event):
    today = datetime.now().date()
    end_date = today + timedelta(
        days=3
    )  # also scrape meetings for the next 3 days to capture meetings spanning multiple days
    scraper = MECSumMinistMeetingsScraper(start_date=today, end_date=end_date, stop_event=stop_event)
    return scraper.scrape()


def scrape_belgian_parliament_meetings(stop_event: multiprocessing.synchronize.Event):
    today = datetime.now().date()
    return run_belgian_parliament_scraper(start_date=today, end_date=today, stop_event=stop_event)


def send_daily_newsletter(stop_event: multiprocessing.synchronize.Event):
    users = supabase.auth.admin.list_users()
    ids = [user.id for user in users]

    logger.info(f"Sending daily newsletter to {len(ids)} users")

    for user_id in ids:
        if stop_event.is_set():
            logger.error(
                f"Stopping newsletter sending due to stop event. Newsletters not sent: {len(ids) - ids.index(user_id)}"
            )
            return

        subscribed = supabase.table("profiles").select("subscribed_newsletter").eq("id", user_id).execute()
        if subscribed.data and subscribed.data[0]["subscribed_newsletter"] is True:
            Newsletter.send_newsletter_to_user(user_id)


def scrape_mec_prep_bodies_meetings(stop_event: multiprocessing.synchronize.Event):
    today = datetime.now().date()
    end_date = today + timedelta(
        days=3
    )  # also scrape meetings for the next 3 days to capture meetings spanning multiple days
    scraper = MECPrepBodiesMeetingsScraper(start_date=today, end_date=end_date, stop_event=stop_event)
    return scraper.scrape()


def scrape_weekly_agenda(stop_event: multiprocessing.synchronize.Event):
    today = datetime.now().date()
    scraper = WeeklyAgendaScraper(start_date=today, end_date=today, stop_event=stop_event)
    return scraper.scrape()


def scrape_austrian_parliament_meetings(stop_event: multiprocessing.synchronize.Event):
    today = datetime.now().date()
    return run_scraper(start_date=today, end_date=today, stop_event=stop_event)


def scrape_polish_presidency_meetings(stop_event: multiprocessing.synchronize.Event):
    today = datetime.now().date()
    scraper = PolishPresidencyMeetingsScraper(start_date=today, end_date=today, stop_event=stop_event)
    return scraper.scrape()


def scrape_spanish_commission_meetings(stop_event: multiprocessing.synchronize.Event):
    today = datetime.now().date()
    scraper = SpanishCommissionScraper(date=today, stop_event=stop_event)
    return scraper.scrape()


def scrape_bundestag_plenary_protocols(stop_event: multiprocessing.synchronize.Event):
    today = datetime.now().date()
    scraper = BundestagPlenarprotokolleScraper(stop_event=stop_event)
    return scraper.scrape(start_date=today, end_date=today)


def scrape_bundestag_drucksachen(stop_event: multiprocessing.synchronize.Event):
    today = datetime.now().date()
    scraper = BundestagDrucksachenScraper(stop_event=stop_event)
    return scraper.scrape(start_date=today, end_date=today)


def scrape_tweets(stop_event: multiprocessing.synchronize.Event):
    usernames = ["EU_Commission", "EUCouncil", "epc_eu", "Euractiv"]
    scraper = TweetScraper(usernames=usernames, stop_event=stop_event)
    return scraper.scrape()


def scrape_legislative_observatory(stop_event: multiprocessing.synchronize.Event):
    scraper = LegislativeObservatoryScraper(stop_event=stop_event)
    return scraper.scrape()


def clean_up_embeddings(stop_event: multiprocessing.synchronize.Event):
    embedding_cleanup(stop_event=stop_event)


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

    scheduler.register("send_daily_newsletter", send_daily_newsletter, schedule.every().day.at("04:30"))
    scheduler.register("clean_up_embeddings", clean_up_embeddings, schedule.every().day.at("04:40"))
    scheduler.register("scrape_tweets", scrape_tweets, schedule.every().day.at("04:50"))
