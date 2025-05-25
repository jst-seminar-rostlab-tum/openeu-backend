import datetime
import re
from collections.abc import Generator
from datetime import date, timedelta
from typing import Callable, Optional

import scrapy
from parsel import Selector
from pydantic import BaseModel
from rapidfuzz import fuzz
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response

from app.core.supabase_client import supabase
from app.data_sources.scraper_base import ScraperBase, ScraperResult
from scripts.embedding_generator import embed_row

# ------------------------------
# Data Model
# ------------------------------


class AgendaEntry(BaseModel):
    type: str
    date: str
    time: Optional[str]
    title: str
    committee: Optional[str]
    location: Optional[str]
    description: Optional[str]
    embedding_input: Optional[str]
    embedding: Optional[list[float]]


# ------------------------------
# Scrapy Spider
# ------------------------------


class WeeklyAgendaSpider(scrapy.Spider):
    """
    A Scrapy spider for scraping the weekly agenda of the European Parliament,
    extracting event details like type, date, time, title, and description for a specified date range.
    """

    name = "weekly_agenda_spider"
    custom_settings = {"LOG_LEVEL": "INFO"}

    def __init__(
        self, start_date: date, end_date: date, result_callback: Optional[Callable[[list[AgendaEntry]], None]] = None
    ):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.result_callback = result_callback
        self.entries: list[AgendaEntry] = []

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        """
        Generate requests for each week in the specified date range.
        """
        week_start = self.start_date
        while week_start <= self.end_date:
            iso_year, iso_week, _ = week_start.isocalendar()
            url = f"https://www.europarl.europa.eu/news/en/agenda/weekly-agenda/{iso_year}-{iso_week:02d}"
            yield scrapy.Request(url=url, callback=self.parse_week, meta={"week_start": week_start})
            week_start += timedelta(weeks=1)

    def closed(self, reason):
        """
        Called when the spider is closed. This is where we can handle the results.
        """
        if self.result_callback:
            self.result_callback(self.entries)

    def parse_week(self, response: Response):
        """
        Parse the weekly agenda page to extract detailed event information for each day.
        This involves iterating through the days of the week and processing individual events
        to gather relevant details such as type, date, time, title, committee, location, and description.
        """

        # Extract the week start date from the response meta
        current_week = response.meta["week_start"]
        print(f"Currently parsing week: {current_week}")

        # Iterate through each day in the week
        for day in response.css("li[id^=agenda-day]"):
            day_date_text = day.css("time::attr(datetime)").get()
            if not day_date_text:
                continue
            day_date = datetime.datetime.strptime(day_date_text, "%Y-%m-%d").date()
            print(f"Scraping day: {day_date}")

            # Iterate through each event in the day's agenda
            for event in day.css("li.ep_gridrow"):
                class_attr = event.attrib.get("class", "")

                # if there are no events of this type, skip
                if "ep-layout_noevent" in class_attr:
                    continue
                # if this is not an event, skip
                if "ep-layout_event" not in class_attr:
                    continue

                event_type = self.get_event_type(event)
                parser = self.get_parser_for_type(event_type)

                if parser:
                    entry = parser(event, day_date, event_type)
                    if entry:
                        if isinstance(entry, AgendaEntry):
                            self.store_entry(entry)
                        elif isinstance(entry, list):
                            for e in entry:
                                self.store_entry(e)

    # --------------------------------
    # Helper Functions
    # --------------------------------

    def get_event_type(self, event: Selector) -> str:
        """
        Extract the event type from the event's class attribute.
        The event type is determined by the class name that starts with "ep-layout_event_".
        """
        class_attr = event.attrib.get("class", "")
        for cls in class_attr.split():
            if cls.startswith("ep-layout_event_"):
                return cls.replace("ep-layout_event_", "")
        return "unknown"

    def get_parser_for_type(self, event_type: str) -> Optional[Callable]:
        """
        Get the appropriate parser function based on the event type.
        """
        return {
            "plenary-session": self.parse_plenary_session,
            "president-diary": self.parse_president_diary,
            "conference-of-presidents": self.parse_default_event,
            "press-conferences": self.parse_press_conferences,
            "conciliation-committee": self.parse_default_event,
            "committee-meetings": self.parse_committee_meetings,
            "delegations": self.parse_delegation_event,
            "public-hearings": self.parse_default_event,
            "other-events": self.parse_other_event,
            "official-visits": self.parse_default_event,
            "solemn-sittings": self.parse_default_event,
        }.get(event_type, self.parse_default_event)

    def check_for_duplicate(self, entry: AgendaEntry) -> bool:
        """
        Check if an AgendaEntry already exists in Supabase for the same date and title.
        Returns True if a duplicate is found, False otherwise.
        """
        try:
            # Query Supabase for existing entries with the same date
            result = supabase.table("weekly_agenda").select("id, title").eq("date", entry.date).execute()
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

    def store_entry(self, entry: AgendaEntry) -> bool:
        """
        This function is for storing AgendaEntry to Supabase.
        If no duplicate is found, upserts the entry to Supabase and stores embedding.
        """
        """ 
        TODO: we should add this workflow into store_entry funtion in ScraperBase: 
        check_for_duplicate, store entry, embed
        """
        try:
            if self.check_for_duplicate(entry):
                self.logger.info(f"Duplicate entry found, skipping: {entry.title}")
                return False

            # no duplicate found, proceed to store the entry
            response = supabase.table("weekly_agenda").upsert(entry.model_dump()).execute()
            inserted = response.data[0]  # The inserted record with auto-generated id

            # Embed using the actual database ID
            # TODO: embed data in embedding input column
            if entry.description and inserted:
                embed_row("weekly_agenda", str(inserted["id"]), "description", entry.description)

            return True

        except Exception as e:
            self.logger.error(f"Failed to store entry: {entry.title}, Error: {e}")
            return False

    # ---------------------------------
    # Different Parsers for Event Types
    # ---------------------------------

    def parse_plenary_session(self, event: Selector, date: date, event_type: str) -> list[AgendaEntry]:
        entries = []

        time_range = event.css("div.ep-layout_date time::text").get()
        location = event.css("div.ep-subtitle span.ep_name::text").get()

        for block in event.css("ol.ep-m_product li.ep_gridrow"):
            header = block.css("h4::text").get()
            title = header.strip() if header else ""

            # Option 1: Try <p> tags
            topic_parts = block.css("p::text").getall()

            # Option 2: If <p> not found, fallback to span.ep_name inside ep-p_text
            if not topic_parts:
                topic_parts = block.css("div.ep-p_text span.ep_name::text").getall()

            topic = "; ".join(p.strip() for p in topic_parts if p.strip())

            procedures = block.css("a::text").re(r"\d{4}/\d{4}\(\w+\)")
            if procedures:
                topic += " | Procedures: " + ", ".join(procedures)

            embedding_input = f"{title} {date.isoformat()} {time_range or ''} {location or ''} {topic}".strip()

            entries.append(
                AgendaEntry(
                    type=event_type,
                    date=date.isoformat(),
                    time=time_range.strip() if time_range else None,
                    title=title,
                    committee=None,
                    location=location.strip() if location else None,
                    description=topic if topic else None,
                    embedding_input=embedding_input,
                    embedding=None,  # Embedding will be handled later
                )
            )

        return entries

    def parse_president_diary(self, event: Selector, date: date, event_type: str) -> list[AgendaEntry]:
        entries = []

        for p in event.css("p.ep-wysiwig_paragraph::text"):
            full_text = p.get().strip()
            if not full_text:
                continue

            # Try to split time (e.g., "11:00 ...")
            time_match = re.match(r"^(\d{2}:\d{2})\s+(.*)", full_text)
            if time_match:
                time, text = time_match.groups()
            else:
                time, text = None, full_text

            embedding_input = f"{text} {date.isoformat()} {time or ''}".strip()

            entries.append(
                AgendaEntry(
                    type=event_type,
                    date=date.isoformat(),
                    time=time,
                    title=text,
                    committee=None,
                    location=None,
                    description=None,
                    embedding_input=embedding_input,
                    embedding=None,  # Embedding will be handled later
                )
            )

        return entries

    def parse_press_conferences(self, event: Selector, date: datetime.date, event_type: str) -> list[AgendaEntry]:
        entries = []

        for item in event.css("ol.ep_gridcolumn.ep-m_product > li.ep_gridrow"):
            time = item.css("div.ep-layout_date time::text").get()
            title = item.css("div.ep-layout_text span.ep_name::text").get()
            location = item.css("div.ep-layout_location span.ep_name::text").get()

            paragraphs = item.css(".ep-layout_text .ep-a_text p, .ep-layout_text .ep-a_text div")
            parts = []
            for p in paragraphs:
                text = " ".join(p.css("*::text").getall()).strip()
                if text:
                    parts.append(text)

            description = "; ".join(parts) if parts else None

            embedding_input = (
                f"{title or ''} {date.isoformat()} {time or ''} {location or ''} {description or ''}".strip()
            )

            entry = AgendaEntry(
                date=date.isoformat(),
                time=time.strip() if time else None,
                title=title.strip() if title else "Untitled",
                type=event_type,
                committee=None,
                location=location,
                description=description,
                embedding_input=embedding_input,
                embedding=None,  # Embedding will be handled later
            )
            entries.append(entry)

        return entries

    def parse_committee_meetings(self, event: Selector, date: datetime.date, event_type: str) -> list[AgendaEntry]:
        entries = []

        for item in event.css("ol.ep_gridcolumn.ep-m_product > li.ep_gridrow"):
            time = item.css("div.ep-layout_date time::text").get()
            location = item.css("div.ep-layout_location span.ep_name::text").get()

            committee = item.css("div.ep-layout_committee abbr::attr(title)").get()

            title = item.css("div.ep-layout_text span.ep_name::text").get()

            # Description: combine all paragraphs + list items
            paragraphs = item.css(
                ".ep-layout_text .ep-a_text p, .ep-layout_text .ep-a_text ul, .ep-layout_text .ep-a_text ol"
            )
            parts = []
            for p in paragraphs:
                text = " ".join(p.css("*::text").getall()).strip()
                if text:
                    parts.append(text)

            description = "; ".join(parts) if parts else None

            embedding_input = (
                f"{title or ''} {date.isoformat()} {time or ''} "
                f"{committee or ''} {location or ''} {description or ''}"
            ).strip()

            entry = AgendaEntry(
                date=date.isoformat(),
                time=time.strip() if time else None,
                title=title.strip() if title else "Untitled",
                type=event_type,
                committee=committee.strip() if committee else None,
                location=location.strip() if location else None,
                description=description,
                embedding_input=embedding_input,
                embedding=None,  # Embedding will be handled later
            )

            entries.append(entry)

        return entries

    def parse_delegation_event(self, event: Selector, date: date, event_type: str) -> Optional[AgendaEntry]:
        """
        Parses a 'Delegations' agenda event.
        Extracts the event title and descriptive paragraphs.
        """
        try:
            # Title: real agenda title under ep-layout_text > span.ep_name
            title = event.css("div.ep-layout_text span.ep_name::text").get()
            title = title.strip() if title else "Delegation"

            # Combine full inner text from each paragraph (includes text + link text)
            paragraph_nodes = event.css("div.ep-a_text p.ep-wysiwig_paragraph")
            paragraph_texts = ["".join(p.css("::text").getall()).strip() for p in paragraph_nodes]
            topic = " ".join(paragraph_texts)

            embedding_input = f"{title} {date.isoformat()} {topic}".strip()

            return AgendaEntry(
                type=event_type,
                date=date.isoformat(),
                time=None,
                title=title,
                committee=None,
                location=None,
                description=topic,
                embedding_input=embedding_input,
                embedding=None,  # Embedding will be handled later
            )

        except Exception as e:
            self.logger.error(f"Failed to parse delegation event: {e}")
            return None

    def parse_other_event(self, event: Selector, date: datetime.date, event_type: str) -> list[AgendaEntry]:
        entries = []

        # Each <li class="ep_gridrow"> represents a sub-event
        for item in event.css("ol.ep-m_product > li.ep_gridrow"):
            # Extract time if present
            time_text = item.css(".ep-layout_date time::text").get()

            # Extract title
            title = item.css(".ep-layout_text .ep_name::text").get()

            # Extract description paragraphs
            description_items = item.css(".ep-layout_text .ep-a_text li")
            parts = []

            for desc in description_items:
                text = " ".join(desc.css("::text").getall()).strip()
                link = desc.css("a::attr(href)").get()
                if link:
                    text += f" ({link})"
                if text:
                    parts.append(text)

            description = "; ".join(parts) if parts else None

            embedding_input = f"{title or ''} {date.isoformat()} {time_text or ''} {description or ''}".strip()

            entry = AgendaEntry(
                date=date.isoformat(),
                time=time_text.strip() if time_text else None,
                title=title.strip() if title else "Untitled",
                type=event_type,
                committee=None,
                location=None,
                description=description,
                embedding_input=embedding_input,
                embedding=None,  # Embedding will be handled later
            )
            entries.append(entry)

        return entries

    def parse_default_event(self, event: Selector, date: date, event_type: str) -> Optional[AgendaEntry]:
        """
        Parses a default event type from the agenda.
        """
        try:
            time = event.css("div.ep-layout_date time::text").get()
            committee = event.css("div.ep-layout_committee abbr::attr(title)").get()
            title = event.css("div.ep-layout_text span.ep_name::text").get()
            location = event.css("div.ep-layout_location span.ep_name::text").get()
            topics = event.css("div.ep-a_text li::text").getall()

            # Validate required fields
            if not title or not date:
                self.logger.warning(f"Skipping event due to missing required fields: title={title}, date={date}")
                return None

            desc = "; ".join(t.strip() for t in topics) if topics else None
            embedding_input = (
                f"{title or ''} {date.isoformat()} {time or ''} {committee or ''} {location or ''} {desc or ''}".strip()
            )

            return AgendaEntry(
                type=event_type,
                date=date.isoformat(),
                time=time.strip() if time else None,
                title=title.strip() if title else "Untitled",
                committee=committee.strip() if committee else None,
                location=location.strip() if location else None,
                description=desc.strip() if desc else None,
                embedding_input=embedding_input,
                embedding=None,  # Embedding will be handled later
            )
        except Exception as e:
            self.logger.error(f"Error parsing default event on {date}: {e}")
            return None


# ------------------------------
# Scraper Base Implementation
# ------------------------------


class WeeklyAgendaScraper(ScraperBase):
    """
    A scraper for the weekly agenda of the European Parliament that implements Scraper Base Interface.
    """

    def __init__(self, start_date: date, end_date: date):
        super().__init__(table_name="weekly_agenda")
        self.start_date = start_date
        self.end_date = end_date
        self.entries: list[AgendaEntry] = []

    def scrape_once(self, last_entry, **kwargs) -> ScraperResult:
        try:
            process = CrawlerProcess(settings={"LOG_LEVEL": "INFO"})
            process.crawl(
                WeeklyAgendaSpider,
                start_date=self.start_date,
                end_date=self.end_date,
                result_callback=self._collect_entry,
            )
            process.start()
            return ScraperResult(success=True, last_entry=self.entries[-1] if self.entries else None)
        except Exception as e:
            return ScraperResult(success=False, error=e)

    def _collect_entry(self, entries: list[AgendaEntry]):
        for entry in entries:
            store_result = self.store_entry(entry.model_dump())
            if store_result is None:
                self.entries.append(entry)


# ------------------------------
# Testing
# ------------------------------


def scrape_agenda(start_date: date, end_date: date) -> list[AgendaEntry]:
    """
    This function initializes a Scrapy CrawlerProcess, sets up the WeeklyAgendaSpider
    with the provided start_date and end_date, and collects the scraped results
    into a list of AgendaEntry objects.

    Args:
        start_date (date): The start date of the scraping range.
        end_date (date): The end date of the scraping range.

    Returns:
        list[AgendaEntry]: A list of AgendaEntry objects containing the scraped agenda data.

    Raises:
        ValueError: If the start_date is after the end_date.
    """
    if start_date > end_date:
        raise ValueError("start_date must be before or equal to end_date")

    results: list[AgendaEntry] = []

    def collect_results(entries):
        results.extend(entries)

    process = CrawlerProcess()
    process.crawl(WeeklyAgendaSpider, start_date=start_date, end_date=end_date, result_callback=collect_results)
    process.start()

    return results


if __name__ == "__main__":
    print("Scraping weekly agenda...")

    # Example: scrape from week 20 to 21
    start = datetime.date(2024, 11, 18)
    end = datetime.date(2025, 5, 26)

    entries = scrape_agenda(start_date=start, end_date=end)
    print(f"Total entries scraped: {len(entries)}")
