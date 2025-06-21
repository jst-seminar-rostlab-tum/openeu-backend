import logging
import math
import re
from collections.abc import AsyncGenerator, Generator
from datetime import date
from typing import Callable, Optional
from urllib.parse import urlencode

import scrapy
from parsel import Selector
from pydantic import BaseModel
from rapidfuzz import fuzz
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response

from app.core.supabase_client import supabase

# type: ignore[attr-defined]
from app.data_sources.scraper_base import ScraperBase, ScraperResult

"""
This file contains a Scrapy spider to scrape MEP meetings from the European Parliament website.
The file can be run as a standalone script to test the scraping functionality.

Table of contents:
1. Data Models
2. Scrapy Spider
3. Scraping Function
4. Database Functions
5. Main Function for Testing
"""

MEP_MEETINGS_BASE_URL = "https://www.europarl.europa.eu/meps/en/search-meetings"
MEP_MEETINGS_TABLE_NAME = "mep_meetings"
MEP_MEETING_ATTENDEES_TABLE_NAME = "mep_meeting_attendees"
MEP_MEETING_ATTENDEE_MAPPING_TABLE_NAME = "mep_meeting_attendee_mapping"


# ------------------------------
# Data Models
# ------------------------------


class MEPMeetingAttendee(BaseModel):
    name: str
    transparency_register_url: Optional[str]


class MEPMeeting(BaseModel):
    """
    Represents a meeting of a European Parliament member.
    Attributes:
        title: The title or subject of the meeting.
        member_name: The name of the European Parliament member involved in the meeting.
        meeting_date: Date of the meeting in "YYYY-MM-DD" format.
        meeting_location: The location where the meeting took place.
        member_capacity: The role or capacity in which the member participated, e.g., "Member", "Committee chair", or
        "Shadow rapporteur" procedure_reference: Reference to the parliamentary procedure related to the meeting, if any
            Typically an Interinstitutional Procedure Identifier like "2023/0001(COD)".
        associated_committee_or_delegation: The committee or delegation associated with the meeting.
        attendees: List of attendees at the meeting.
    """

    title: str
    member_name: str
    meeting_date: str
    meeting_location: str
    member_capacity: str
    procedure_reference: Optional[str]
    associated_committee_or_delegation_code: Optional[str]
    associated_committee_or_delegation_name: Optional[str]
    attendees: list[MEPMeetingAttendee]
    embedding_input: Optional[str] = None


# ------------------------------
# Scrapy Spider
# ------------------------------


class MEPMeetingsSpider(scrapy.Spider):
    name = "meetings_spider"
    custom_settings = {"LOG_LEVEL": "ERROR"}

    def __init__(
        self, start_date: date, end_date: date, result_callback: Optional[Callable[[list[MEPMeeting]], None]] = None
    ):
        super().__init__()
        self.start_date: date = start_date
        self.end_date: date = end_date
        self.result_callback: Optional[Callable[[list[MEPMeeting]], None]] = result_callback
        self.meetings: list[MEPMeeting] = []

    async def start(self) -> AsyncGenerator[scrapy.Request, None]:
        """
        Start the spider.
        """
        yield self.scrape_page(0)

    def scrape_page(self, page: int) -> scrapy.Request:
        """
        Initiate a request to scrape a specific page of meetings.
        :param page: The page number to scrape.
        :return: A Scrapy Request object.
        """
        params = {
            "fromDate": self.start_date.strftime("%d/%m/%Y"),
            "toDate": self.end_date.strftime("%d/%m/%Y"),
            "page": page,
        }
        return scrapy.Request(
            url=MEP_MEETINGS_BASE_URL + "?" + urlencode(params),
            callback=self.parse_search_results_page,
            meta={"page": page},
        )

    def closed(self, reason):
        """Called when the spider is closed. Returns the results via the result_callback."""
        if self.result_callback:
            self.result_callback(self.meetings)

    def parse_search_results_page(self, response: Response) -> Generator[scrapy.Request, None, None]:
        """
        Parse the search results page and extract meeting information.
        :param response: The response object from the search results page.
        :return: Generator yielding Request objects for pagination.
        """
        total_pages = self.parse_total_pages_num(response)

        for meeting_sel in response.css(".erpl_document"):
            meeting = self.parse_meeting(meeting_sel)
            self.meetings.append(meeting)

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
        max_results_per_query = 10000
        # although website states 10000 results maximum, &page=51 returns an error
        unofficial_max_pages = 51

        result_text = response.css("#meetingSearchResultCounterText::text").get()
        # example text: "Showing 10 of 100 results"
        total_results = 0
        if result_text:
            match = re.search(r"of (\d+)", result_text)
            if match:
                total_results = int(match.group(1))
        total_pages = math.ceil(total_results / num_results_per_page)

        is_first_page = response.meta["page"] == 0
        if is_first_page and total_results == max_results_per_query:
            logging.warning(
                f"Warning: The number of results is the maximum possible ({max_results_per_query}). "
                "This likely indicates that the date range is too large and that there are more results "
                "available."
            )
        if is_first_page and total_pages > unofficial_max_pages:
            logging.warning(
                f"Warning: The number of pages is larger than the unofficial maximum "
                f"({unofficial_max_pages}). "
                "This likely indicates that the date range is too large and that there are more results"
                " available."
            )
            total_pages = unofficial_max_pages

        return total_pages

    def parse_meeting(self, sel: Selector) -> MEPMeeting:
        """
        Parse a meeting entry from the search results.
        :param sel: The selector for the meeting entry.
        :return: A Meeting object.
        """

        def extract_text(css_sel):
            return sel.css(css_sel + "::text").get(default="").strip()

        # Extract general meeting details
        title = extract_text(".erpl_document-title .t-item")
        member_name = extract_text(".erpl_document-subtitle-member")
        meeting_date = sel.css("time::attr(datetime)").get(default="").strip()
        meeting_location = extract_text(".erpl_document-subtitle-location")
        member_capacity = extract_text(".erpl_document-subtitle-capacity")
        procedure_code = extract_text(".erpl_document-subtitle-reference")
        associated_cmte_code = sel.css(".erpl_badge::text").get()
        associated_cmte_name = sel.css(".erpl_badge::attr(title)").get()

        # Extract list of attendees
        attendees = []
        for node in sel.css(".erpl_document-subtitle-author"):
            # Extract the transparency register URL (if it exists)
            transparancy_register_url = node.css("a::attr(href)").get()
            # Attendees may be listed as links or spans
            # names of attendees with tranparency_register_urls are in <a> tags
            # names of attendees without tranparency_register_urls are in <span> tags
            name_from_link = node.css("a::text").get(default="").strip()
            name_from_span = node.css("::text").get(default="").strip()
            name = name_from_link or name_from_span

            attendees.append(MEPMeetingAttendee(name=name, transparency_register_url=transparancy_register_url))

        associated_cmte_embedding = ""
        if associated_cmte_name and associated_cmte_code:
            associated_cmte_embedding = f"{associated_cmte_code} ({associated_cmte_name})"
        elif associated_cmte_name:
            associated_cmte_embedding = associated_cmte_name

        return MEPMeeting(
            title=title,
            member_name=member_name,
            meeting_date=meeting_date,
            meeting_location=meeting_location,
            member_capacity=member_capacity,
            procedure_reference=procedure_code if procedure_code else None,
            associated_committee_or_delegation_code=associated_cmte_code if associated_cmte_code else None,
            associated_committee_or_delegation_name=associated_cmte_name if associated_cmte_name else None,
            attendees=attendees,
            embedding_input=f'"{title}", on {meeting_date}, at {meeting_location}, by {member_name} ({member_capacity})'
            + f"{(', referenced procedure: ' + procedure_code) if procedure_code else ''}"
            + f"{(', committee: ' + associated_cmte_embedding) if associated_cmte_embedding else ''}"
            + f", attendees: [{', '.join(att.name for att in attendees)}]",
        )


# ------------------------------
# Scraper Base Implementation
# ------------------------------


class MEPMeetingsScraper(ScraperBase):
    """
    A scraper for the MEP meetings of the European Parliament that implements Scraper Base Interface.
    """

    logger = logging.getLogger("MEPMeetingsScraper")

    def __init__(self, start_date: date, end_date: date):
        super().__init__(table_name=MEP_MEETINGS_TABLE_NAME)
        self.start_date = start_date
        self.end_date = end_date
        self.entries: list[MEPMeeting] = []

    def scrape_once(self, last_entry, **kwargs) -> ScraperResult:
        try:
            process = CrawlerProcess(
                settings={
                    "LOG_LEVEL": "INFO",
                    "USER_AGENT": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36"
                    " (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36",
                }
            )
            process.crawl(
                MEPMeetingsSpider,
                start_date=self.start_date,
                end_date=self.end_date,
                result_callback=self._collect_entry,
            )
            process.start()
            return ScraperResult(success=True, last_entry=self.entries[-1] if self.entries else None)
        except Exception as e:
            return ScraperResult(success=False, error=e)

    def _collect_entry(self, entries: list[MEPMeeting]):
        for entry in entries:
            upsert_id = self._check_for_duplicate(entry)

            try:
                self._insert_meeting(entry, upsert_id=upsert_id)
                self.entries.append(entry)

            except Exception as e:
                self.logger.error(f"Error inserting meeting {entry.title}: {e}")
                continue

    def _check_for_duplicate(self, entry: MEPMeeting) -> Optional[str]:
        """
        Check if a MEPMeeting already exists in Supabase for the same date and very similar title.
        Returns the ID of the duplicate if found, None otherwise.
        """
        try:
            # Query Supabase for existing entries with the same date
            result = (
                supabase.table(MEP_MEETINGS_TABLE_NAME)
                .select("id, title")
                .eq("meeting_date", entry.meeting_date)
                .execute()
            )
            existing_entries = result.data or []

            # Check for fuzzy match
            for existing in existing_entries:
                existing_title = existing["title"]
                if fuzz.token_sort_ratio(existing_title, entry.title) > 90:
                    return existing["id"]  # Duplicate found

            # No duplicates found
            return None

        except Exception as e:
            self.logger.error(f"Error checking for duplicates: {e}")
            return None

    def _insert_meeting(self, meeting: MEPMeeting, upsert_id: Optional[str] = None) -> None:
        """
        Insert a meeting into the database and map attendees to it.
        :param meeting: The meeting object to insert.
        :return: The ID of the inserted meeting.
        """
        # Insert meeting
        meeting_dict = meeting.model_dump()
        if upsert_id:
            meeting_dict["id"] = upsert_id
        meeting_dict.pop("attendees")
        meeting_id = self.store_entry_returning_id(meeting_dict)

        if upsert_id:
            # If we are updating an existing meeting, we need to delete old attendee mappings
            supabase.table(MEP_MEETING_ATTENDEE_MAPPING_TABLE_NAME).delete().eq("meeting_id", meeting_id).execute()

        for attendee in meeting.attendees:
            # Insert attendee if not already exists
            attendee_id = self._create_or_get_existing_attendee_id(attendee)

            # Map attendee to meeting
            supabase.table(MEP_MEETING_ATTENDEE_MAPPING_TABLE_NAME).insert(
                {"meeting_id": meeting_id, "attendee_id": attendee_id}
            ).execute()

    def _create_or_get_existing_attendee_id(self, attendee: MEPMeetingAttendee) -> str:
        """
        Create a new attendee or get the existing one.
        :param attendee: The attendee object to insert or find.
        :return: The ID of the attendee.
        """
        if attendee.transparency_register_url:
            existing_attendee_id = (
                supabase.table(MEP_MEETING_ATTENDEES_TABLE_NAME)
                .select("id")
                .eq("transparency_register_url", attendee.transparency_register_url)
                .limit(1)
                .execute()
            )
        else:
            # Fallback: try by name if URL missing (not ideal for deduplication)
            existing_attendee_id = (
                supabase.table(MEP_MEETING_ATTENDEES_TABLE_NAME)
                .select("id")
                .eq("name", attendee.name)
                .limit(1)
                .execute()
            )

        if existing_attendee_id.data:
            attendee_id = existing_attendee_id.data[0]["id"]
        else:
            # Insert new attendee
            result = supabase.table(MEP_MEETING_ATTENDEES_TABLE_NAME).insert(attendee.model_dump()).execute()
            attendee_id = result.data[0]["id"]

        return attendee_id


# ------------------------------
# Main Function for Testing
# ------------------------------


if __name__ == "__main__":
    import datetime

    print("Scraping meetings...")

    scraper = MEPMeetingsScraper(start_date=datetime.date(2025, 3, 15), end_date=datetime.date(2025, 3, 16))
    result = scraper.scrape()
    meetings = scraper.entries
    if result.success:
        print(f"Scraping completed successfully. {len(meetings)} meetings found.")
    else:
        print(f"Scraping failed: {result.error}")

    # pprint(meetings)
    print(f"Total meetings scraped: {len(meetings) if meetings else 0}")
