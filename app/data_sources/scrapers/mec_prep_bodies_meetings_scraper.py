import asyncio
import logging
import re
from datetime import date
from typing import Optional
from urllib.parse import urlencode

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from pydantic import BaseModel

# type: ignore[attr-defined]
from app.data_sources.scraper_base import ScraperBase, ScraperResult

"""
This file contains a crawl4ai-scraper to scrape the European Council's website for MEC Summit Ministerial Meeting data.
The spider extracts meeting URLs, titles, and dates, and stores them in a Supabase database.
The file can be run as a standalone script to test the scraping functionality.

Table of contents:
1. Data Model
2. Util Functions
3. Scraping Logic
4. Database Functions
5. Main Function for Testing
"""

logger = logging.getLogger(__name__)


MEC_MEETINGS_BASE_URL = "https://www.consilium.europa.eu/en/meetings/calendar/"
MEETINGS_DETAIL_URL_PREFIX = "https://www.consilium.europa.eu/en/meetings/"
MEC_SUMMIT_MINISTERIAL_MEETING_TABLE_NAME = "mec_prep_bodies_meeting"


# ------------------------------
# Data Model
# ------------------------------


class MECPrepBodiesMeeting(BaseModel):
    id: int
    url: str
    prep_body_abbr: str
    title: str
    meeting_date: str
    meeting_time: str
    meeting_location: str


class MECPrepBodiesMeetingsScraper(ScraperBase):
    def __init__(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        """Initialize the scraper."""
        super().__init__(MEC_SUMMIT_MINISTERIAL_MEETING_TABLE_NAME, max_retries, retry_delay)
        self.events: list[MECPrepBodiesMeeting] = []
        self.start_date = start_date
        self.end_date = end_date

    # ------------------------------
    # Scraping Logic
    # ------------------------------

    def _get_largest_page_number(self, links: list[dict]) -> int:
        """
        Extracts the largest page number from a list of links.

        Args:
            links (list[dict]): List of link dictionaries.

        Returns:
            int: The largest page number found, or 0 if none found.
        """
        page_number_pattern = re.compile(r"page=(\d+)")
        largest_page = max(
            (
                int(match.group(1))
                for link in links
                if "page=" in link["href"]
                if (match := page_number_pattern.search(link["href"]))
            ),
            default=0,
        )
        return largest_page

    async def _scrape_meetings_by_page(
        self,
        start_date: date,
        end_date: date,
        page: int,
        crawler: AsyncWebCrawler,
        last_entry: MECPrepBodiesMeeting,
    ) -> tuple[list[MECPrepBodiesMeeting], int, ScraperResult | None]:
        """
        Scrape meetings on page <page> from the European Council's website for a specific date range.
        Args:
            start_date (date): The start date for the meeting search.
            end_date (date): The end date for the meeting search.
            page (int): The page number to scrape.
            crawler (AsyncWebCrawler): The web crawler instance.
        Returns:
            tuple: A tuple containing a list of found meetings and the largest page number.
        """
        logger.info(f"Scraping page {page} for meetings between {start_date} and {end_date}")
        found_meetings = []
        params = {
            "DateFrom": start_date.strftime("%Y/%m/%d"),
            "DateTo": end_date.strftime("%Y/%m/%d"),
            "category": "mpo",
            "page": page,
        }
        url = MEC_MEETINGS_BASE_URL + "?" + urlencode(params)
        config = CrawlerRunConfig()
        crawler_result = await crawler.arun(url=url, crawler_config=config)
        internal_links = crawler_result.links.get("internal", [])
        links_to_meetings = [x for x in internal_links if x["href"].startswith(MEETINGS_DETAIL_URL_PREFIX)]

        largest_page = self._get_largest_page_number(links_to_meetings)

        # matches meetings like /meetings/mpo/2025/5/coreper-1-permanent-representatives-committee-(349018)/
        meeting_url_pattern = re.compile(r"/meetings/([a-z0-9-]+)/(\d{4})/(\d{1,2})/.*\((\d+)\)/", re.IGNORECASE)

        for link in links_to_meetings:
            meeting_url = link["href"]
            match = meeting_url_pattern.search(url)
            if match:
                prep_body_abbr = match.group(1)
                # meeting_start_date_year = match.group(2)
                # meeting_start_date_month = match.group(3)
                meeting_id = match.group(4)

                crawler_result = await crawler.arun(url=meeting_url, crawler_config=config)

                # todo: parse location, date and time

                meeting = MECPrepBodiesMeeting(
                    id=meeting_id,
                    prep_body_abbr=prep_body_abbr,
                    url=link["href"],
                    title=link["text"],
                    # meeting_date=meeting_date.isoformat(),
                    # meeting_end_date=meeting_end_date.isoformat() if meeting_end_date else None,
                )

                if last_entry and meeting == last_entry:
                    continue

                found_meetings.append(meeting)
                scraper_error_result = self.store_entry(meeting.model_dump())
                if scraper_error_result:
                    return (found_meetings, largest_page, scraper_error_result)
                self.last_entry = meeting

        return (found_meetings, largest_page, None)

    async def scrape_once_async(self, last_entry: MECPrepBodiesMeeting) -> ScraperResult:
        found_meetings: list[MECPrepBodiesMeeting] = []
        current_page = 1
        largest_known_page = 1

        start_date = self.start_date
        end_date = self.end_date
        if not start_date or not end_date:
            raise ValueError("Missing start_date or end_date")
        if start_date > end_date:
            raise ValueError("start_date must be before end_date")

        async with AsyncWebCrawler() as crawler:
            while current_page <= largest_known_page:
                (meetings_on_page, largest_known_page, scraper_error_result) = await self._scrape_meetings_by_page(
                    start_date=start_date, end_date=end_date, page=current_page, crawler=crawler, last_entry=last_entry
                )
                found_meetings.extend(meetings_on_page)
                if scraper_error_result:
                    return scraper_error_result
                current_page += 1

        # Remove duplicates based on id
        # duplicates occurr when a meeting spans multiple days and is therefore listed multiple times
        found_meetings = list({(meeting.id): meeting for meeting in found_meetings}.values())

        return ScraperResult(success=True, error=None, last_entry=self.last_entry)

    def scrape_once(self, last_entry, **args) -> ScraperResult:
        """
        Scrape mec meetings and store them in the database.
        :param start_date: The start date for the meeting search.
        :param end_date: The end date for the meeting search.
        """
        try:
            return asyncio.run(self.scrape_once_async(last_entry))
        except Exception as e:
            logger.error(f"Error while scraping and storing meetings: {e}")
            return ScraperResult(False, e, None)


# ------------------------------
# Main Function for Testing
# ------------------------------


if __name__ == "__main__":
    print("Scraping and storing mec meetings...")
    scraper = MECPrepBodiesMeetingsScraper(start_date=date(2025, 5, 17), end_date=date(2025, 6, 17))
    result: ScraperResult = scraper.scrape()
    print(result)
