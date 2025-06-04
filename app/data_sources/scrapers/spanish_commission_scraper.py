# ------------------------------
# Imports
# ------------------------------
import datetime
import logging
from collections.abc import Generator
from typing import Callable, Optional

import scrapy
from pydantic import BaseModel
from rapidfuzz import fuzz
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response

from app.core.deepl_translator import translator
from app.core.supabase_client import supabase
from app.data_sources.scraper_base import ScraperBase, ScraperResult
from app.data_sources.translator.translator import DeepLTranslator

# ------------------------------
# Data Model
# ------------------------------


class CommissionAgendaEntry(BaseModel):
    date: str
    time: Optional[str]
    title: str
    title_en: Optional[str] = None
    location: Optional[str]
    location_en: Optional[str] = None
    description: Optional[str]
    description_en: Optional[str] = None
    url: Optional[str]
    embedding_input: Optional[str]
    links: Optional[dict[str, str]] = None


# ------------------------------
# Scrapy Spider
# ------------------------------


class SpanishCommissionSpider(scrapy.Spider):
    name = "spanish_commission_spider"
    custom_settings = {"LOG_LEVEL": "INFO"}

    def __init__(self, date: datetime.date, result_callback: Optional[Callable] = None):
        self.date = date
        self.result_callback = result_callback
        self.entries: list[CommissionAgendaEntry] = []
        self.translator = DeepLTranslator(translator)
        super().__init__()

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        url = f"https://www.congreso.es/en/agenda?p_p_id=agenda&p_p_lifecycle=0&p_p_state=normal&p_p_mode=view&_agenda_mvcPath=cambiaragenda&_agenda_tipoagenda=1&_agenda_dia={self.date.day:02d}&_agenda_mes={self.date.month:02d}&_agenda_anio={self.date.year}"
        yield scrapy.Request(url=url, callback=self.parse_day)

    def closed(self, reason):
        if self.result_callback:
            self.result_callback(self.entries)

    def parse_day(self, response: Response):
        for row in response.css("table.table-agenda tbody tr"):
            time = row.css("td:nth-child(1)::text").get(default="").strip()
            content_divs = row.css("td:nth-child(2) div")

            description_div = content_divs[0] if len(content_divs) > 0 else None
            location_div = content_divs[1] if len(content_divs) > 1 else None

            # Extract all <a> tag links into a dictionary
            links = {}
            primary_url = None
            if description_div:
                for a in description_div.css("a"):
                    label = a.css("::text").get("").lower().strip().replace(" ", "_")
                    href = a.css("::attr(href)").get()
                    if href:
                        full_url = response.urljoin(href)
                        if not primary_url:
                            primary_url = full_url
                        if label in links:
                            links[label + "_2"] = full_url
                        else:
                            links[label] = full_url

            # Gather text
            description_parts = description_div.css("::text").getall() if description_div else []
            description_text = " ".join(part.strip() for part in description_parts if part.strip())
            # description_en = self.translator.translate(description_text).text if description_text else ""

            # Title logic
            title = description_div.css("a::text").get() if description_div else "Untitled"
            if not title and description_text:
                title = description_text
                description_text = ""
            elif not title:
                title = "Untitled"
            # title_en = self.translator.translate(title).text if title else "Untitled"

            location = (location_div.css("::text").get() or "").strip() if location_div else None
            # location_en = self.translator.translate(location).text if location else None

            embedding_input = (
                f"{title} {self.date.isoformat()} {time} {location or ''} {description_text or ''}".strip()
            )

            entry = CommissionAgendaEntry(
                date=self.date.isoformat(),
                time=time,
                title=title.strip(),
                # title_en=title_en,
                location=location,
                # location_en=location_en,
                description=description_text,
                # description_en=description_en,
                url=primary_url,
                embedding_input=embedding_input,
                links=links or None,
            )

            self.entries.append(entry)


# ------------------------------
# Scraper Base Implementation
# ------------------------------


class SpanishCommissionScraper(ScraperBase):
    def __init__(self, date: datetime.date):
        super().__init__("spanish_commission_meetings")
        self.date = date
        self.entries: list[CommissionAgendaEntry] = []
        self.logger = logging.getLogger(__name__)

    def scrape_once(self, last_entry, **kwargs) -> ScraperResult:
        try:
            process = CrawlerProcess()
            process.crawl(
                SpanishCommissionSpider,
                date=self.date,
                result_callback=self._collect_entry,
            )
            process.start()
            return ScraperResult(success=True)
        except Exception as e:
            return ScraperResult(success=False, error=e)

    def _collect_entry(self, entries: list[CommissionAgendaEntry]):
        for entry in entries:
            if self.check_for_duplicate(entry):
                self.logger.info(f"Skipped duplicate: {entry.title}")
                continue

            store_result = self.store_entry(entry.model_dump())
            if store_result is None:
                self.entries.append(entry)

    def check_for_duplicate(self, entry: CommissionAgendaEntry) -> bool:
        """
        Check if an AgendaEntry already exists in Supabase for the same date and title.
        Returns True if a duplicate is found, False otherwise.
        """
        try:
            # Query Supabase for existing entries with the same date
            result = supabase.table("spanish_commission_meetings").select("id, title").eq("date", entry.date).execute()
            existing_entries = result.data or []

            # Check for fuzzy match
            for existing in existing_entries:
                existing_title = existing["title"]
                if fuzz.token_sort_ratio(existing_title, entry.title) > 90:
                    self.logger.info(f"Duplicate found: {entry.title} matches {existing_title}")
                    return True  # Duplicate found

            # No duplicates found
            return False

        except Exception as e:
            self.logger.error(f"Error checking for duplicates: {e}")
            return False


# ------------------------------
# Testing
# ------------------------------


def scrape_agenda(date: datetime.date) -> list[CommissionAgendaEntry]:
    results: list[CommissionAgendaEntry] = []

    def collect_results(entries):
        results.extend(entries)

    process = CrawlerProcess()
    process.crawl(SpanishCommissionSpider, date=date, result_callback=collect_results)
    process.start()

    return results


if __name__ == "__main__":
    print("Scraping Spanish Commision Agenda...")
    date = datetime.date(2025, 5, 29)

    """
    entries = scrape_agenda(date)
    print(f"Total entries scraped: {len(entries)}")
    """

    scraper = SpanishCommissionScraper(date)
    result = scraper.scrape_once(last_entry=None)
    if result.success:
        print(f"Scraping completed successfully. Total entries stored: {len(scraper.entries)}")
    else:
        print(f"Scraping failed with error: {result.error}")
