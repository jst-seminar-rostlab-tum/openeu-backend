import asyncio
import logging
import re
from datetime import date, datetime
import multiprocessing
from typing import Optional
from urllib.parse import urlencode

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from parsel import Selector
from pydantic import BaseModel

# type: ignore[attr-defined]
from app.data_sources.scraper_base import ScraperBase, ScraperResult

"""
This file contains a crawl4ai-scraper to scrape the European Council's website for MEC Preparatory Bodies Meeting data.
The spider extracts the meeting details and stores them in a Supabase database.
The file can be run as a standalone script to test the scraping functionality.

Table of contents:
1. Imports
2. Constants
3. Data Model
4. Scraper Class
5. Main Function for Testing
"""

logger = logging.getLogger(__name__)


MEC_MEETINGS_BASE_URL = "https://www.consilium.europa.eu/en/meetings/calendar/"
MEETINGS_DETAIL_URL_PREFIX = "https://www.consilium.europa.eu/en/meetings/"
MEC_PREP_BODIES_MEETING_TABLE_NAME = "mec_prep_bodies_meeting"


# ------------------------------
# Data Model
# ------------------------------


class MECPrepBodiesMeeting(BaseModel):
    id: str
    url: str
    title: str
    meeting_timestamp: str
    meeting_location: str
    embedding_input: str


class MECPrepBodiesMeetingsScraper(ScraperBase):
    def __init__(
        self,
        stop_event: multiprocessing.synchronize.Event,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        """Initialize the scraper."""
        super().__init__(MEC_PREP_BODIES_MEETING_TABLE_NAME, stop_event, max_retries, retry_delay)
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
        found_meetings: list[MECPrepBodiesMeeting] = []
        params = {
            "DateFrom": start_date.strftime("%Y/%m/%d"),
            "DateTo": end_date.strftime("%Y/%m/%d"),
            "category": "mpo",
            "page": page,
        }
        url = MEC_MEETINGS_BASE_URL + "?" + urlencode(params)
        config = CrawlerRunConfig(
            # verbose=True,
            # log_console=True,
            # magic=True, # seems to only make bot protection issues worse
            # simulate_user=True, # seems to only make bot protection issues worse
            # override_navigator=True, # seems to only make bot protection issues worse
            # user_agent_mode="random", # seems to only make bot protection issues worse
        )
        crawler_result = await crawler.arun(url=url, config=config)
        if not crawler_result.success:
            logger.error(f"Failed to scrape page {page}: {crawler_result.error}")
            return (found_meetings, 0, ScraperResult(False, crawler_result.error, None))
        if "Checking your browser" in crawler_result.html:
            logger.error(f"Bot protection detected for page {page}. Therefore, we cannot scrape something now.")
        internal_links = crawler_result.links.get("internal", [])
        largest_page = self._get_largest_page_number(internal_links)

        selector = Selector(text=crawler_result.html)
        meeting_results: list[tuple[datetime, str]] = []
        date_groups = selector.css("div.gsc-excerpt-list__item")
        for date_group in date_groups:
            # extract the date from the date group, format is "17 May 2025"
            date_text = date_group.css("div.gsc-excerpt-list__item-date.gsc-heading--md::text").get()
            if not date_text:
                continue
            try:
                date = datetime.strptime(date_text.strip(), "%d %B %Y")
            except ValueError as e:
                logger.error(f"Failed to parse date '{date_text}': {e}")
                continue

            # extract the meeting links from the date group
            meeting_links = date_group.css("a.gsc-excerpt-item__link")
            for link in meeting_links:
                url = link.attrib.get("href")
                url_already_exists = any(existing_url == url for (_, existing_url) in meeting_results)
                # only save the first occurrence of a url (same url can occur multiple times
                # if meeting spans multiple days)
                if url_already_exists:
                    continue
                meeting_results.append((date, url))

        # matches meetings like /meetings/mpo/2025/5/coreper-1-permanent-representatives-committee-(349018)/
        meeting_url_pattern = re.compile(r"meetings/mpo/\d{4}/\d{1,2}/.*\((\d+)\)", re.IGNORECASE)

        for date, url in meeting_results:
            try:
                match = meeting_url_pattern.search(url)
                if match:
                    meeting_id = str(match.group(1))

                    title = link["text"].strip()

                    meeting = MECPrepBodiesMeeting(
                        id=meeting_id,
                        url=link["href"],
                        title=title,
                        meeting_timestamp=date.isoformat(),
                        meeting_location="",  # room_label + " (" + building_label + " building)",
                        embedding_input=f"{title}, {date.isoformat()}",  # , {room_label} in {building_label} building",
                    )

                    if last_entry and meeting == last_entry:
                        continue

                    found_meetings.append(meeting)
                    scraper_error_result = self.store_entry(meeting.model_dump())
                    if scraper_error_result:
                        return (found_meetings, largest_page, scraper_error_result)
                    self.last_entry = meeting
            except Exception as e:
                logger.error(f"Error processing meeting link {link['href']}: {e}")
                continue

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

        while current_page <= largest_known_page:
            if self.stop_event.is_set():
                return ScraperResult(
                    success=False,
                    error=Exception("Scrape stopped by external stop event"),
                    last_entry=self.last_entry,
                )

            # crawl the page with a new AsyncWebCrawler instance
            # crawl4ai docs recommend reusing the same crawler instance for multiple pages,
            # but this is the only found way to avoid running into bot protection issues
            async with AsyncWebCrawler() as crawler:
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
        """
        try:
            return asyncio.run(self.scrape_once_async(last_entry))
        except Exception as e:
            logger.error(f"Error while scraping and storing meetings: {e}")
            return ScraperResult(success=False, error=e)


# ------------------------------
# Main Function for Testing
# ------------------------------


if __name__ == "__main__":
    print("Scraping and storing mect preparatory bodies meetings...")
    scraper = MECPrepBodiesMeetingsScraper(
        start_date=date(2025, 5, 17), end_date=date(2025, 5, 18), stop_event=multiprocessing.Event()
    )
    result: ScraperResult = scraper.scrape()
    print(result)
