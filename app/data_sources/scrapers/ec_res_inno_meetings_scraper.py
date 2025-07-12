import asyncio
import logging
import math
import multiprocessing
import re
from collections.abc import AsyncGenerator, Generator
from datetime import date
from typing import Callable, Optional
from urllib.parse import urlencode

import scrapy
from parsel import Selector
from pydantic import BaseModel
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response

# type: ignore[attr-defined]
from app.data_sources.scraper_base import ScraperBase, ScraperResult

"""
This file contains a scraper for Research and Innovation meetings from the European Commission website.
The file can be run as a standalone script to test the scraping functionality.

Table of contents:
1. Data Models
2. Scrapy Spider
3. Scraper Base Implementation
4. Main Function for Testing
"""

EC_RES_INNO_MEETINGS_BASE_URL = "https://research-and-innovation.ec.europa.eu/events/upcoming-events_en"
EC_RES_INNO_MEETINGS_RSS_URL = "https://research-and-innovation.ec.europa.eu/node/4/rss_en"
EC_RES_INNO_MEETINGS_TABLE_NAME = "ec_res_inno_meetings"


# ------------------------------
# Data Models
# ------------------------------


class EcResInnoMeeting(BaseModel):
    id: Optional[str] = None
    title: str
    meeting_url: str
    start_date: str
    end_date: Optional[str] = None
    location: str
    event_type: str
    description: str
    subjects: list[str] = []
    embedding_input: str


class EcResInnoMeetingSearchResult(BaseModel):
    # id: Optional[str] = None
    title: str
    meeting_url: str
    start_date: str
    end_date: Optional[str] = None
    location: str
    event_type: str
    # description: str
    # subjects: list[str] = []
    # embedding_input: str


class EcResInnoMeetingRss(BaseModel):
    id: Optional[str] = None
    title: str
    meeting_url: str
    # start_date: str
    # end_date: Optional[str] = None
    # location: str
    event_type: str
    description: str
    subjects: list[str] = []
    # embedding_input: str


# ------------------------------
# Scrapy Spider
# ------------------------------


class EcResInnoMeetingsSpider(scrapy.Spider):
    """A Scrapy spider for scraping Research and Innovation meetings from the European Commission website.
    This spider scrapes meeting information from the RSS feed and the main events page and merges the results since
    both sources contain different information about the same meetings.
    """

    name = "meetings_spider"
    custom_settings = {"LOG_LEVEL": "ERROR", "CONCURRENT_REQUESTS": 1}

    def __init__(
        self,
        start_date: date,
        end_date: date,
        stop_event: multiprocessing.synchronize.Event,
        result_callback: Optional[Callable[[list[EcResInnoMeeting]], None]] = None,
    ):
        super().__init__()
        self.start_date: date = start_date
        self.end_date: date = end_date
        self.result_callback: Optional[Callable[[list[EcResInnoMeeting]], None]] = result_callback
        self.meetings: list[EcResInnoMeeting] = []
        self.rssMeetings: list[EcResInnoMeetingRss] = []
        self.stop_event = stop_event
        self.rss_scrapes_done = 0

    async def start(self) -> AsyncGenerator[scrapy.Request, None]:
        """
        Start the spider.
        """
        rss_requests = []
        async for rss_request in self.scrape_rss(start_date=self.start_date, end_date=self.end_date):
            rss_requests.append(rss_request)

        # Yield all RSS requests first
        for request in rss_requests:
            yield request

        # Wait for the RSS scraping to complete
        while len(rss_requests) > self.rss_scrapes_done:
            await asyncio.sleep(1)

        # After all RSS requests are yielded, start scraping the search results pages
        yield self.scrape_page(0)

    async def scrape_rss(self, start_date: date | None, end_date: date | None) -> AsyncGenerator[scrapy.Request, None]:
        """
        Initiate a request to scrape the RSS feed for meetings.
        :return: A generator potentially yielding additional Scrapy Requests if needed.
        :param start_date: The start date for filtering meetings.
        :param end_date: The end date for filtering meetings.
        """
        if self.stop_event.is_set():
            raise scrapy.exceptions.CloseSpider("Stop event is set, stopping the spider.")

        if start_date is None:
            start_date = self.start_date
        if end_date is None:
            end_date = self.end_date

        params = {
            "f[0]": f"oe_event_event_date:bt|{start_date.strftime('%Y-%m-%dT%H:%M:%S%z')}"
            f"|{end_date.strftime('%Y-%m-%dT%H:%M:%S%z')}",
        }

        async def parse_page(response: Response) -> AsyncGenerator[scrapy.Request, None]:
            async for request in self.parse_rss_page(response, start_date=start_date, end_date=end_date):
                yield request

        yield scrapy.Request(
            url=EC_RES_INNO_MEETINGS_RSS_URL + "?" + urlencode(params),
            callback=parse_page,
        )

    async def parse_rss_page(
        self, response: Response, start_date: date, end_date: date
    ) -> AsyncGenerator[scrapy.Request, None]:
        """
        Parse the RSS feed and extract meeting information.
        Starts additional scraping requests if the RSS feed might not contain all meetings within the date range.
        :param start_date: The start date for filtering meetings.
        :param end_date: The end date for filtering meetings.
        :param response: The response object from the RSS feed.
        :return: Generator potentially yielding additional Request objects if needed to scrape all meetings.
        """
        items = response.xpath("//item")

        max_items_per_page = 30
        if len(items) == max_items_per_page:
            # might be more items, so we need to scrape date range in two parts
            middle_date = start_date + (end_date - start_date) // 2
            async for request in self.scrape_rss(start_date, middle_date):
                yield request
            async for request in self.scrape_rss(middle_date, end_date):
                yield request
            return

        for item in items:
            title = item.xpath("title/text()").get(default="").strip()
            description = item.xpath("description/text()").get(default="").strip()
            description = re.sub(r"<.*?>", "", description)  # remove html tags from description
            link = item.xpath("link/text()").get(default="")
            atom_id = item.xpath("*[local-name()='id']/text()").get(default="")
            event_type = item.xpath(
                "category[@domain='http://publications.europa.eu/resource/authority/public-event-type']/text()"
            ).get(default="")
            subjects = item.xpath("category[@domain='http://data.europa.eu/uxp/det']/text()").getall()

            meeting = EcResInnoMeetingRss(
                id=atom_id,
                title=title,
                description=description,
                meeting_url=link,
                event_type=event_type,
                subjects=subjects,
            )
            self.rssMeetings.append(meeting)
        self.rss_scrapes_done += 1

    def scrape_page(self, page: int) -> scrapy.Request:
        """
        Initiate a request to scrape a specific meetings search results page.
        :param page: The page number to scrape.
        :return: A Scrapy Request object.
        """
        if self.stop_event.is_set():
            raise scrapy.exceptions.CloseSpider("Stop event is set, stopping the spider.")

        params = {
            "f[0]": f"oe_event_event_date:bt|{self.start_date.strftime('%Y-%m-%dT%H:%M:%S%z')}"
            f"|{self.end_date.strftime('%Y-%m-%dT%H:%M:%S%z')}",
            "page": page,
        }
        return scrapy.Request(
            url=EC_RES_INNO_MEETINGS_BASE_URL + "?" + urlencode(params),
            callback=self.parse_search_results_page,
            meta={"page": page},
        )

    def closed(self, reason):
        """Called when the spider is closed. Returns the results via the result_callback."""
        # warn if rssMeetings and meetings have different lengths
        # in that case, we might have incomplete data after merging rssMeetings and meetings
        if len(self.rssMeetings) != len(self.meetings):
            self.logger.warning(
                f"RSS meetings count ({len(self.rssMeetings)}) does not match"
                f" parsed meetings count ({len(self.meetings)})."
            )
        if self.result_callback:
            self.result_callback(self.meetings)

    def parse_search_results_page(self, response: Response) -> Generator[scrapy.Request, None, None]:
        """
        Parse the search results page and extract meeting information.
        :param response: The response object from the search results page.
        :return: Generator yielding Request objects for pagination.
        """

        total_pages = self.parse_total_pages_num(response)

        for meeting_sel in response.css("article.ecl-content-item.ecl-content-item--inline"):
            meeting = self.parse_meeting(meeting_sel)
            # merge with existing meeting if it has the same link
            matching_meetings = (m for m in self.rssMeetings if meeting.meeting_url in m.meeting_url)
            existing_meeting = next(matching_meetings, None)
            if existing_meeting is None:
                # try to find an existing meeting with the same title
                existing_meeting = next((m for m in self.rssMeetings if m.title == meeting.title), None)
            if existing_meeting is None:
                pass
            meeting_to_store: EcResInnoMeeting = EcResInnoMeeting(
                id=existing_meeting.id if existing_meeting else None,
                title=meeting.title,
                start_date=meeting.start_date,
                end_date=meeting.end_date,
                location=meeting.location,
                meeting_url=existing_meeting.meeting_url if existing_meeting else meeting.meeting_url,
                event_type=meeting.event_type,
                description=existing_meeting.description if existing_meeting else "",
                subjects=existing_meeting.subjects if existing_meeting else [],
                embedding_input=f'"{meeting.title}" on {meeting.start_date}'
                f"{(' until ' + meeting.end_date) if meeting.end_date else ''}, location: {meeting.location}"
                + f"{', description: "' + existing_meeting.description + '"' if existing_meeting else ''}",
            )
            self.meetings.append(meeting_to_store)

        current_page = response.meta["page"]
        if current_page < total_pages:
            yield self.scrape_page(current_page + 1)

    def parse_total_pages_num(self, response: Response) -> int:
        """
        Parse the total number of pages from the search results.
        :param response: The response object from the search results page.
        :return: The total number of pages.
        """
        num_results_per_page = 10

        result_text = response.css(
            "div.ecl-col-s-12.ecl-col-m-9 div h4.ecl-u-type-heading-4.ecl-u-mb-s span::text"
        ).getall()[1]
        # example text: "Showing results 10 to 16"
        total_results = 0
        if result_text:
            match = re.search(r"(\d+)", result_text)
            if match:
                total_results = int(match.group(1))
        total_pages = math.ceil(total_results / num_results_per_page)

        return total_pages

    def extract_dates(self, day: str, month: str, year: str) -> tuple[date, Optional[date]]:
        separator = "-"

        def month_to_number(month_str: str) -> int:
            month_str = month_str.upper()
            months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
            return months.index(month_str) + 1 if month_str in months else 0

        start_date_day = day.split(separator)[0].strip()
        start_date_month = month.split(separator)[0].strip()
        start_date_year = year.split(separator)[0].strip()
        start_date = date(int(start_date_year), month_to_number(start_date_month), int(start_date_day))

        end_date = None
        if "-" in day:
            # If the day is a range, we need to extract the end date
            end_date_day = day.split(separator)[1].strip()
            end_date_month = month.split(separator)[1].strip() if separator in month else start_date_month
            end_date_year = year.split(separator)[1].strip() if separator in year else start_date_year
            end_date = (
                date(int(end_date_year), month_to_number(end_date_month), int(end_date_day)) if end_date_day else None
            )

        return start_date, end_date

    def parse_meeting(self, sel: Selector) -> EcResInnoMeetingSearchResult:
        """
        Parse a meeting entry from the search results.
        :param sel: The selector for the meeting entry.
        :return: A Meeting object.
        """

        def extract_text(css_sel):
            return sel.css(css_sel + "::text").get(default="").strip()

        title = extract_text(".ecl-content-block__title .ecl-link")
        if title == "":
            # sometimes the title is in a different structure
            title = extract_text(".ecl-content-block__title .ecl-link__label")

        # Extract date from time element (format: DD MM YYYY)
        date_day = extract_text(".ecl-date-block__day")  # e.g. "15" or "15-18"
        date_month = extract_text(".ecl-date-block__month")  # "JUN" or "JUN-JUL"
        date_year = extract_text(".ecl-date-block__year")  # e.g. "2025" or "2025-2026"
        (start_date, end_date) = self.extract_dates(date_day, date_month, date_year)

        # Extract location
        location = extract_text(
            ".ecl-u-d-flex.ecl-u-align-items-center.ecl-unordered-list__item.ecl-u-mh-none.ecl-u-ph-none"
        )

        # Extract event type
        event_type = extract_text(".ecl-content-block__primary-meta-item")
        meeting_url = sel.css("a.ecl-link::attr(href)").get(default="")

        if title == "":
            title = "No title found"

        return EcResInnoMeetingSearchResult(
            title=title,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat() if end_date else None,
            location=location,
            meeting_url=meeting_url,
            event_type=event_type,
        )


# ------------------------------
# Scraper Base Implementation
# ------------------------------


class EcResInnoMeetingsScraper(ScraperBase):
    """
    A scraper for the Innovation & Research meetings of the European Council that implements Scraper Base Interface.
    """

    logger = logging.getLogger("EcResInnoMeetingsScraper")

    def __init__(self, start_date: date, end_date: date, stop_event: multiprocessing.synchronize.Event):
        super().__init__(table_name=EC_RES_INNO_MEETINGS_TABLE_NAME, stop_event=stop_event)
        self.start_date = start_date
        self.end_date = end_date
        self.entries: list[EcResInnoMeeting] = []

    def scrape_once(self, last_entry, **kwargs) -> ScraperResult:
        try:
            process = CrawlerProcess(
                settings={
                    "LOG_LEVEL": "INFO",
                    "USER_AGENT": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36"
                    " (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
                    "CONCURRENT_REQUESTS": 1,
                }
            )
            process.crawl(
                EcResInnoMeetingsSpider,
                start_date=self.start_date,
                end_date=self.end_date,
                result_callback=self._collect_entry,
                stop_event=self.stop_event,
            )
            process.start()
            return ScraperResult(success=True, last_entry=self.entries[-1] if self.entries else None)
        except Exception as e:
            return ScraperResult(success=False, error=e)

    def _collect_entry(self, entries: list[EcResInnoMeeting]):
        for entry in entries:
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
    print("Scraping meetings...")

    scraper = EcResInnoMeetingsScraper(
        start_date=date(2025, 1, 15), end_date=date(2025, 6, 16), stop_event=multiprocessing.Event()
    )
    result = scraper.scrape()
    meetings = scraper.entries
    if result.success:
        print(f"Scraping completed successfully. {len(meetings)} meetings found.")
    else:
        print(f"Scraping failed: {result.error}")

    # pprint(meetings)
    print(f"Total meetings scraped: {len(meetings) if meetings else 0}")
