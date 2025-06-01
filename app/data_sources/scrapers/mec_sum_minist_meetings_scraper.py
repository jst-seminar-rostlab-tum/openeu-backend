import asyncio
import calendar
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
MEC_SUMMIT_MINISTERIAL_MEETING_TABLE_NAME = "mec_summit_ministerial_meeting"


# ------------------------------
# Data Model
# ------------------------------


class MECSummitMinisterialMeeting(BaseModel):
    url: str
    title: str
    meeting_date: str
    meeting_end_date: Optional[str]
    category_abbr: Optional[str]
    embedding_input: Optional[str] = None


class _MeetingDateParser:
    @staticmethod
    def parse_meeting_dates(year_str: str, month_str: str, day_range_str: str) -> tuple[date, Optional[date]]:
        """
        Parses meeting start and optional end dates from a year, month, and day range string.

        Args:
            year (str): The year as a 4-digit string.
            month (str): The month as a 2-digit string.
            day_range (str): A day or range like "3" or "30-2".

        Returns:
            tuple[date, Optional[date]]: (start_date, end_date)
        """
        year = int(year_str)
        month = int(month_str)

        if "-" in day_range_str:
            start_day_str, end_day_str = day_range_str.split("-")
            start_day = int(start_day_str)
            end_day = int(end_day_str)

            # Detect if this is a cross-month situation
            if start_day > end_day:
                # Start date in previous month
                start_month = month - 1
                start_year = year
                if start_month < 1:
                    start_month = 12
                    start_year -= 1

                # Validate start day within correct number of days in the month
                last_day_of_prev_month = calendar.monthrange(start_year, start_month)[1]
                if start_day > last_day_of_prev_month:
                    raise ValueError(f"Invalid start day {start_day} for month {start_month}/{start_year}")

                start_date = date(start_year, start_month, start_day)
                end_date = date(year, month, end_day)
            else:
                start_date = date(year, month, start_day)
                end_date = date(year, month, end_day)
        else:
            start_day = int(day_range_str)
            start_date = date(year, month, start_day)
            end_date = None

        return start_date, end_date

    def test_parse_meeting_dates(self):
        # Case 1: Single day
        start, end = self._parse_meeting_dates("2024", "05", "3")
        assert start == date(2024, 5, 3)
        assert end is None

        # Case 2: Normal range within same month
        start, end = self._parse_meeting_dates("2024", "05", "3-5")
        assert start == date(2024, 5, 3)
        assert end == date(2024, 5, 5)

        # Case 3: Range spanning two months (e.g., May 31 – June 2)
        start, end = self._parse_meeting_dates("2024", "06", "31-2")
        assert start == date(2024, 5, 31)
        assert end == date(2024, 6, 2)

        # Case 4: Weirdly reversed but same month (should still parse correctly)
        start, end = self._parse_meeting_dates("2024", "05", "5-3")
        assert start == date(2024, 4, 5)
        assert end == date(2024, 5, 3)

        # Case 5: spanning 2 years
        start, end = self._parse_meeting_dates("2024", "01", "31-2")
        assert start == date(2023, 12, 31)
        assert end == date(2024, 1, 2)


class MECSumMinistMeetingsScraper(ScraperBase):
    def __init__(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        """Initialize the scraper.
        Args:
            start_date (Optional[date]): The start date for scraping meetings.
            end_date (Optional[date]): The end date for scraping meetings.
            max_retries (int): Maximum number of retries for failed requests.
            retry_delay (float): Delay between retries in seconds.
        """
        super().__init__(MEC_SUMMIT_MINISTERIAL_MEETING_TABLE_NAME, max_retries, retry_delay)
        self.events: list[MECSummitMinisterialMeeting] = []
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
        last_entry: MECSummitMinisterialMeeting,
    ) -> tuple[list[MECSummitMinisterialMeeting], int, ScraperResult | None]:
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
            "category": "meeting",
            "page": page,
        }
        url = MEC_MEETINGS_BASE_URL + "?" + urlencode(params)
        config = CrawlerRunConfig()
        crawler_result = await crawler.arun(url=url, crawler_config=config)
        internal_links = crawler_result.links.get("internal", [])
        links_to_meetings = [x for x in internal_links if x["href"].startswith(MEETINGS_DETAIL_URL_PREFIX)]

        largest_page = self._get_largest_page_number(links_to_meetings)

        # matches patterns like /meetings/agrifish/2024/05/3-5/
        meeting_url_pattern = re.compile(r"/meetings/([a-z0-9-]+)/(\d{4})/(\d{2})/([\d\-]+)/")

        for link in links_to_meetings:
            match = meeting_url_pattern.search(link["href"])
            if match:
                meeting_date, meeting_end_date = _MeetingDateParser.parse_meeting_dates(
                    year_str=match.group(2),
                    month_str=match.group(3),
                    day_range_str=match.group(4),
                )

                meeting_title = link["text"].strip()
                embedding_input = f'"{meeting_title}"'
                if meeting_end_date is not None:
                    embedding_input += f", from {meeting_date.isoformat()} to {meeting_end_date.isoformat()}"
                else:
                    embedding_input += f", on {meeting_date.isoformat()}"

                meeting = MECSummitMinisterialMeeting(
                    url=link["href"],
                    title=meeting_title,
                    meeting_date=meeting_date.isoformat(),
                    meeting_end_date=meeting_end_date.isoformat() if meeting_end_date else None,
                    category_abbr=match.group(1),
                    embedding_input=embedding_input,
                )

                if last_entry and meeting == last_entry:
                    continue

                found_meetings.append(meeting)
                scraper_error_result = self.store_entry(meeting.model_dump(), on_conflict="url", embedd_entries=False)
                if scraper_error_result:
                    return (found_meetings, largest_page, scraper_error_result)
                self.last_entry = meeting

        return (found_meetings, largest_page, None)

    async def scrape_once_async(self, last_entry: MECSummitMinisterialMeeting) -> ScraperResult:
        """
        Asynchronously scrapes MEC Summit Ministerial Meetings and stores them in the database.
        """
        found_meetings: list[MECSummitMinisterialMeeting] = []
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

        # Remove duplicates based on URL and title
        # duplicates occurr when a meeting spans multiple days and is therefore listed multiple times
        found_meetings = list({(meeting.url, meeting.title): meeting for meeting in found_meetings}.values())

        return ScraperResult(success=True, error=None, last_entry=self.last_entry)

    def scrape_once(self, last_entry, **args) -> ScraperResult:
        """
        Scrapes MEC Summit Ministerial Meetings and stores them in the database.
        Uses asyncio.run to execute the asynchronous scrape_once_async method.
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
    print("Scraping and storing mec summit and ministerial meetings...")
    scraper = MECSumMinistMeetingsScraper(start_date=date(2025, 5, 17), end_date=date(2025, 6, 17))
    result: ScraperResult = scraper.scrape()
    print(result)
