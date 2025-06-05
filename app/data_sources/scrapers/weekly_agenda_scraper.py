import datetime
import logging
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
                        # If a single AgendaEntry is returned
                        if isinstance(entry, AgendaEntry):
                            self.entries.append(entry)

                        # If a list of AgendaEntries is returned
                        elif isinstance(entry, list):
                            self.entries.extend(entry)

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

    # ---------------------------------
    # Different Parsers for Event Types
    # ---------------------------------

    def parse_plenary_session(self, event: Selector, date: date, event_type: str) -> list[AgendaEntry]:
        entries = []
        global_location = event.css("h3 .ep_subtitle .ep_name::text").get()
        global_location = global_location.strip() if global_location else None

        # Each block for a time slot
        for li in event.css("ol.ep-m_product > li.ep_gridrow"):
            time_text = li.css("div.ep-layout_date time::text").get()
            time_text = time_text.strip() if time_text else None

            # Look for the title inside the first .ep_title span.ep_name (e.g., "Debates")
            title = li.css("div.ep-layout_text .ep_title span.ep_name::text").get()
            title = title.strip() if title else "Untitled"

            # Collect all topic/subtopic text as description
            description_parts = []

            for node in li.css("div.ep-layout_text > *"):
                text_parts = node.xpath(".//text()").getall()
                text = " ".join(t.strip() for t in text_parts if t.strip())
                if text:
                    description_parts.append(text)

            # Combine everything into final description
            description = "; ".join(description_parts)

            embedding_input = (
                f"{title} {date.isoformat()} {time_text or ''} {global_location or ''} {description}".strip()
            )

            entries.append(
                AgendaEntry(
                    type=event_type,
                    date=date.isoformat(),
                    time=time_text,
                    title=title,
                    committee=None,
                    location=global_location,
                    description=description,
                    embedding_input=embedding_input,
                )
            )

        return entries

    def parse_president_diary(self, event: Selector, date: date, event_type: str) -> list[AgendaEntry]:
        entries = []

        for p in event.css("p.ep-wysiwig_paragraph"):
            full_text = " ".join(p.css("*::text").getall()).strip()
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
            )
            entries.append(entry)

        return entries

    def parse_committee_meetings(self, event: Selector, date: datetime.date, event_type: str) -> list[AgendaEntry]:
        # TODO: add links

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
            )

            entries.append(entry)

        return entries

    def parse_delegation_event(self, event: Selector, date: date, event_type: str) -> list[AgendaEntry]:
        """
        Parses a 'Delegations' agenda event.
        Extracts the event title and descriptive paragraphs.
        """
        # TODO: add links
        entries = []

        # Each <li> is a delegation sub-event
        for li in event.css("ol.ep-m_product > li.ep_gridrow"):
            try:
                # Title
                title = li.css("div.ep-layout_text span.ep_name::text").get()
                title = title.strip() if title else "Delegation"

                # Description from <li> inside ep-a_text
                description_container = li.css("div.ep-a_text")
                description_parts = []

                # Loop through both li and p elements
                for node in description_container.css("li, p"):
                    text = " ".join(node.css("::text").getall()).strip()
                    href = node.css("a::attr(href)").get()
                    if href:
                        text += f" ({href})"
                    if text:
                        description_parts.append(text)

                description = " ".join(description_parts) if description_parts else None

                embedding_input = f"{title} {date.isoformat()} {description or ''}".strip()

                entry = AgendaEntry(
                    type=event_type,
                    date=date.isoformat(),
                    time=None,
                    title=title,
                    committee=None,
                    location=None,
                    description=description,
                    embedding_input=embedding_input,
                )

                entries.append(entry)

            except Exception as e:
                self.logger.error(f"Failed to parse a delegation sub-event: {e}")

        return entries

    def parse_other_event(self, event: Selector, date: datetime.date, event_type: str) -> list[AgendaEntry]:
        entries = []

        # Each <li class="ep_gridrow"> represents a sub-event
        for item in event.css("ol.ep-m_product > li.ep_gridrow"):
            # Extract time if present
            time_text = item.css(".ep-layout_date time::text").get()

            # Extract title
            title = item.css(".ep-layout_text .ep_name::text").get()
            location = item.css(".ep-layout_text .ep_subtitle .ep-layout_location .ep_name::text").get()

            # Extract description paragraphs
            # changed li to p.ep-wysiwig_paragraph
            description_items = item.css(".ep-layout_text .ep-a_text p.ep-wysiwig_paragraph")
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
                location=location,
                description=description,
                embedding_input=embedding_input,
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

    logger = logging.getLogger("WeeklyAgendaScraper")

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
            if self.check_for_duplicate(entry):
                self.logger.info(f"Skipped duplicate: {entry.title}")
                continue

            store_result = self.store_entry(entry.model_dump())
            if store_result is None:
                self.entries.append(entry)

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
    start = datetime.date(2025, 4, 7)
    end = datetime.date(2025, 6, 5)

    #   entries = scrape_agenda(start_date=start, end_date=end)
    #   print(f"Total entries scraped: {len(entries)}")

    scraper = WeeklyAgendaScraper(start_date=start, end_date=end)
    result = scraper.scrape_once(last_entry=None)
    if result.success:
        print(f"Scraping completed successfully. Total entries stored: {len(scraper.entries)}")
    else:
        print(f"Scraping failed with error: {result.error}")
