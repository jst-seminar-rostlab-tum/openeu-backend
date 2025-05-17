from app.core.scheduling import scheduler
from app.data_sources.apis.mep import fetch_and_store_current_meps
from app.data_sources.scrapers.bundestag_drucksachen_scraper import scrape_bundestag_plenarprotokolle


def scrape_plenarprotokolle():
    scrape_bundestag_plenarprotokolle("2025-01-01", "2025-04-30")


def setup_scheduled_jobs():
    scheduler.register("fetch_and_store_current_meps", fetch_and_store_current_meps, 10)
    scheduler.register("scrape_bundestag_plenarprotokolle", scrape_plenarprotokolle, 10)
