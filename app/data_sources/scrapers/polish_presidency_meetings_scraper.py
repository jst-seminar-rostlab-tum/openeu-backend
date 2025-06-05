import logging
import re
from collections.abc import AsyncGenerator
from datetime import date
from datetime import datetime as dt
from typing import Callable, Optional
from urllib.parse import urlencode

import scrapy
from pydantic import BaseModel
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response

from app.data_sources.scraper_base import ScraperBase, ScraperResult

"""
This file contains a Scrapy spider to scrape meetings from the Polish EU Presidency website.
The file can be run as a standalone script to test the scraping functionality.

Table of contents:
1. Data Models
2. Scrapy Spider
3. Scraping Function
4. Database Functions
5. Main Function for Testing
"""

POLISH_PRESIDENCY_BASE_URL = "https://polish-presidency.consilium.europa.eu/events/print/"
POLISH_PRESIDENCY_MEETINGS_TABLE_NAME = "polish_presidency_meeting"


# ------------------------------
# Data Models
# ------------------------------


class PolishPresidencyMeeting(BaseModel):
    """
    Represents a meeting of the Polish EU Presidency.
    Attributes:
        id: slug in the meeting URL
        title: The title of the meeting.
        meeting_date: Date of the meeting in "YYYY-MM-DD" format.
        meeting_end_date: Optional end date for meetings that span multiple days.
        meeting_location: The location where the meeting takes place.
        meeting_url: The URL to the meeting details page.
        embedding_input: Combined text for embedding.
    """

    id: str
    title: str
    meeting_date: str
    meeting_end_date: Optional[str] = None
    meeting_location: str
    meeting_url: str
    embedding_input: Optional[str] = None


# ------------------------------
# Scrapy Spider
# ------------------------------


class PolishPresidencyMeetingsSpider(scrapy.Spider):
    name = "polish_presidency_meetings_spider"
    custom_settings = {"LOG_LEVEL": "ERROR"}

    def __init__(
        self,
        start_date: date,
        end_date: date,
        result_callback: Optional[Callable[[list[PolishPresidencyMeeting]], None]] = None,
    ):
        super().__init__()
        self.start_date: date = start_date
        self.end_date: date = end_date
        self.result_callback: Optional[Callable[[list[PolishPresidencyMeeting]], None]] = result_callback
        self.meetings: list[PolishPresidencyMeeting] = []

    async def start(self) -> AsyncGenerator[scrapy.Request, None]:
        """
        Called by Scrapy when the spider starts crawling.
        """
        params = {
            "StartDate": self.start_date.strftime("%Y-%m-%d"),
            "EndDate": self.end_date.strftime("%Y-%m-%d"),
        }
        url = POLISH_PRESIDENCY_BASE_URL + "?" + urlencode(params)
        yield scrapy.Request(url=url, callback=self.parse_meetings)

    def closed(self, reason):
        """Called when the spider is closed. Returns the results via the result_callback."""
        if self.result_callback:
            self.result_callback(self.meetings)

    def parse_meetings(self, response: Response) -> None:
        """
        Parse the meetings from the Polish EU Presidency website.
        :param response: The response object from the events print page.
        """
        # Find all date groups
        date_groups = response.css(".events-group")

        for date_group in date_groups:
            # Extract the date from the date group
            day = date_group.css(".events-group__date-day::text").get("").strip()
            month = date_group.css(".events-group__date-month::text").get("").strip()
            year = self.start_date.year  # Assuming events are in current year

            # Parse the date
            try:
                meeting_date_obj = dt.strptime(f"{day} {month} {year}", "%d %B %Y")
                meeting_date = meeting_date_obj.strftime("%Y-%m-%d")
            except ValueError:
                self.logger.error(f"Failed to parse date: {day} {month} {year}")
                continue

            # Find all meetings in this date group
            meetings = date_group.css("ul > li")

            for meeting in meetings:
                title = meeting.css(".event__title a::text").get("").strip()
                location = meeting.css(".event__location span::text").get("").strip()
                meeting_url = response.urljoin(meeting.css(".event__title a::attr(href)").get(""))
                meeting_slug_match = re.search(r"/([^/]+)/?$", meeting_url)
                meeting_slug = meeting_slug_match.group(1) if meeting_slug_match else None
                if not meeting_slug:
                    self.logger.error(
                        f"Failed to extract meeting slug from meeting with title: {title}, URL: {meeting_url}"
                    )
                    continue
                embedding_input = f'"{title}", on {meeting_date}, in {location}'

                polish_meeting = PolishPresidencyMeeting(
                    id=meeting_slug,
                    title=title,
                    meeting_date=meeting_date,
                    meeting_location=location,
                    meeting_url=meeting_url,
                    embedding_input=embedding_input,
                )

                self.meetings.append(polish_meeting)


# ------------------------------
# Scraper Base Implementation
# ------------------------------


class PolishPresidencyMeetingsScraper(ScraperBase):
    """
    A scraper for the meetings of the Polish EU Presidency that implements Scraper Base Interface.
    """

    logger = logging.getLogger("PolishPresidencyMeetingsScraper")

    def __init__(self, start_date: date, end_date: date):
        super().__init__(table_name=POLISH_PRESIDENCY_MEETINGS_TABLE_NAME)
        self.start_date = start_date
        self.end_date = end_date
        self.entries: list[PolishPresidencyMeeting] = []

    def scrape_once(self, last_entry, **kwargs) -> ScraperResult:
        try:
            process = CrawlerProcess(settings={"LOG_LEVEL": "INFO"})
            process.crawl(
                PolishPresidencyMeetingsSpider,
                start_date=self.start_date,
                end_date=self.end_date,
                result_callback=self._collect_entries,
            )
            process.start()
            return ScraperResult(success=True, last_entry=self.entries[-1] if self.entries else None)
        except Exception as e:
            return ScraperResult(success=False, error=e)

    def _collect_entries(self, entries: list[PolishPresidencyMeeting]):
        # set end date for meetings that appear on multiple days with same id
        filtered_entries = {}
        for entry in entries:
            if entry.id not in filtered_entries:
                filtered_entries[entry.id] = entry
            else:
                # If the meeting already exists, update the end date if it's later
                existing_entry = filtered_entries[entry.id]
                if entry.meeting_date > existing_entry.meeting_date:
                    existing_entry.meeting_end_date = entry.meeting_date
                else:
                    existing_entry.meeting_end_date = existing_entry.meeting_date

        # store entries
        for entry in filtered_entries.values():
            try:
                self.store_entry(entry.model_dump(), embedd_entries=True)
                self.entries.append(entry)
            except Exception as e:
                self.logger.error(f"Error inserting meeting {entry.title}: {e}")
                continue


# ------------------------------
# Main Function for Testing
# ------------------------------


if __name__ == "__main__":
    import datetime

    print("Scraping Polish EU Presidency meetings...")

    scraper = PolishPresidencyMeetingsScraper(start_date=datetime.date(2025, 6, 3), end_date=datetime.date(2025, 6, 3))
    result = scraper.scrape()
    meetings = scraper.entries
    if result.success:
        print(f"Scraping completed successfully. {len(meetings)} meetings found.")
    else:
        print(f"Scraping failed: {result.error}")

    print(f"Total meetings scraped: {len(meetings) if meetings else 0}")

    # Print sample of meetings for verification
    if meetings:
        print("\nSample meetings:")
        for i, meeting in enumerate(meetings[:3]):
            print(f"{i+1}. {meeting.title} - {meeting.meeting_date} - {meeting.meeting_location}")
