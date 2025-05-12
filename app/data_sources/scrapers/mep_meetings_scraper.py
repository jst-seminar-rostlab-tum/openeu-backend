import math
import re
from datetime import date
from typing import Any, Callable, Generator, List, Optional
from urllib.parse import urlencode

import scrapy
from parsel import Selector
from pydantic import BaseModel
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response
from supabase import Client, create_client

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
        member_capacity: The role or capacity in which the member participated, e.g., "Member", "Committee chair", or "Shadow rapporteur"
        procedure_reference: Reference to the parliamentary procedure related to the meeting, if any.
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
    attendees: List[MEPMeetingAttendee]

# ------------------------------
# Scrapy Spider
# ------------------------------


class MEPMeetingsSpider(scrapy.Spider):
    name = "meetings_spider"
    custom_settings = {'LOG_LEVEL': 'ERROR'}

    def __init__(self, start_date: date, end_date: date, result_callback: Optional[Callable[[List[MEPMeeting]], None]] = None):
        super().__init__()
        self.base_url = "https://www.europarl.europa.eu/meps/en/search-meetings?"
        self.start_date: date = start_date
        self.end_date: date = end_date
        self.result_callback: Optional[Callable[[
            List[MEPMeeting]], None]] = result_callback
        self.meetings: List[MEPMeeting] = []

    def start_requests(self) -> Generator[scrapy.Request, Any, None]:
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
        return scrapy.Request(url=self.base_url + urlencode(params), callback=self.parse_search_results_page, meta={'page': page})

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

        current_page = response.meta['page']
        if current_page < total_pages:
            yield self.scrape_page(current_page + 1)

    def parse_total_pages_num(self, response: Response) -> int:
        """
        Parse the total number of pages from the search results.
        :param response: The response object from the search results page.
        :return: The total number of pages.
        """
        NUM_RESULTS_PER_PAGE = 10
        MAX_RESULTS_PER_QUERY = 10000
        # although website states 10000 results maximum, &page=51 returns an error
        INOFFICIAL_MAX_PAGES = 51

        result_text = response.css(
            "#meetingSearchResultCounterText::text").get()
        # example text: "Showing 10 of 100 results"
        total_results = 0
        if result_text:
            match = re.search(r'of (\d+)', result_text)
            if match:
                total_results = int(match.group(1))
        total_pages = math.ceil(total_results / NUM_RESULTS_PER_PAGE)

        is_first_page = response.meta['page'] == 0
        if is_first_page and total_results == MAX_RESULTS_PER_QUERY:
            print(f"Warning: The number of results is the maximum possible ({MAX_RESULTS_PER_QUERY}). "
                  "This likely indicates that the date range is too large and that there are more results available.")
        if is_first_page and total_pages > INOFFICIAL_MAX_PAGES:
            print(f"Warning: The number of pages is larger than the unofficial maximum ({INOFFICIAL_MAX_PAGES}). "
                  "This likely indicates that the date range is too large and that there are more results available.")
            total_pages = INOFFICIAL_MAX_PAGES

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

            attendees.append(
                MEPMeetingAttendee(name=name, transparency_register_url=transparancy_register_url))

        return MEPMeeting(
            title=title,
            member_name=member_name,
            meeting_date=meeting_date,
            meeting_location=meeting_location,
            member_capacity=member_capacity,
            procedure_reference=procedure_code if procedure_code else None,
            associated_committee_or_delegation_code=associated_cmte_code if associated_cmte_code else None,
            associated_committee_or_delegation_name=associated_cmte_name if associated_cmte_name else None,
            attendees=attendees
        )

# ------------------------------
# Scraping Function
# ------------------------------


def scrape_meetings(start_date: date, end_date: date) -> List[MEPMeeting]:
    """
    Scrape meetings from the European Parliament website.

    :param start_date: The start date for the meeting search.
    :param end_date: The end date for the meeting search.
    :return: A list of Meeting objects.
    """

    if start_date > end_date:
        raise ValueError("start_date must be before or equal to end_date")

    results = []

    def collect_results(meetings):
        results.extend(meetings)

    process = CrawlerProcess(settings={'USER_AGENT': 'Mozilla/5.0'})
    process.crawl(MEPMeetingsSpider,
                  start_date=start_date,
                  end_date=end_date,
                  result_callback=collect_results)
    process.start()

    return results


# ------------------------------
# Database Functions
# ------------------------------

def scrape_and_store_meetings(start_date: date, end_date: date):
    """
    Scrape meetings and store them in the database.
    :param start_date: The start date for the meeting search.
    :param end_date: The end date for the meeting search.

    Assumes these tables:
    ```sql
    CREATE TABLE IF NOT EXISTS mep_meetings (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        title text NOT NULL,
        member_name text NOT NULL,
        meeting_date date NOT NULL,
        meeting_location text NOT NULL,
        member_capacity text NOT NULL,
        procedure_reference text,
        associated_committee_or_delegation_code text,
        associated_committee_or_delegation_name text
    );

    CREATE TABLE IF NOT EXISTS mep_meeting_attendees (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        name text NOT NULL,
        transparency_register_url text UNIQUE
    );

    CREATE TABLE IF NOT EXISTS mep_meeting_attendee_mapping (
        meeting_id uuid REFERENCES mep_meetings(id) ON DELETE CASCADE,
        attendee_id uuid REFERENCES mep_meeting_attendees(id) ON DELETE CASCADE,
        PRIMARY KEY (meeting_id, attendee_id)
    );
    ```
    """
    # TODO: set correct Supabase URL and key, without this it won't work
    raise NotImplementedError(
        "Please set the correct Supabase URL and key in the code before running it.")
    SUPABASE_URL = "https://your-project.supabase.co"
    SUPABASE_KEY = "your-supabase-service-role-key"
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    try:

        meetings = scrape_meetings(start_date, end_date)

        # Delete existing meetings in the date range and their attendee_mappings via on delete cascade
        supabase.table("mep_meetings").delete().gte(
            "meeting_date", start_date).lte("meeting_date", end_date).execute()

        for meeting in meetings:
            # Insert each meeting into the database
            insert_meeting(meeting, supabase)
            print(
                f"Inserted meeting: {meeting.title} on {meeting.meeting_date}")
    except Exception as e:
        print(f"Error while scraping and storing meetings: {e}")

    return meetings


def insert_meeting(meeting: MEPMeeting, supabase: Client):
    """
    Insert a meeting into the database and map attendees to it.
    :param meeting: The meeting object to insert.
    :return: The ID of the inserted meeting.
    """
    # Insert meeting
    meeting_dict = meeting.model_dump()
    meeting_dict.pop("attendees")
    response = supabase.table("mep_meetings").insert(meeting_dict).execute()
    meeting_id = response.data[0]["id"]

    for attendee in meeting.attendees:
        # Insert attendee if not already exists
        attendee_id = create_or_get_existing_attendee_id(attendee, supabase)

        # Map attendee to meeting
        supabase.table("mep_meeting_attendee_mapping").insert({
            "meeting_id": meeting_id,
            "attendee_id": attendee_id
        }).execute()


def create_or_get_existing_attendee_id(attendee: MEPMeetingAttendee, supabase: Client) -> str:
    """
    Create a new attendee or get the existing one.
    :param attendee: The attendee object to insert or find.
    :return: The ID of the attendee.
    """
    if attendee.transparency_register_url:
        existing_attendee_id = supabase.table("mep_meeting_attendees").select("id").eq(
            "transparency_register_url", attendee.transparency_register_url).limit(1).execute()
    else:
        # Fallback: try by name if URL missing (not ideal for deduplication)
        existing_attendee_id = supabase.table("mep_meeting_attendees").select(
            "id").eq("name", attendee.name).limit(1).execute()

    if existing_attendee_id.data:
        attendee_id = existing_attendee_id.data[0]["id"]
    else:
        # Insert new attendee
        result = supabase.table(
            "mep_meeting_attendees").insert(attendee.model_dump()).execute()
        attendee_id = result.data[0]["id"]

    return attendee_id

# ------------------------------
# Main Function for Testing
# ------------------------------


if __name__ == "__main__":
    import datetime
    from pprint import pprint

    print("Scraping meetings...")

    meetings = scrape_and_store_meetings(
        start_date=datetime.date(2025, 3, 15),
        end_date=datetime.date(2025, 3, 18)
    )

    # pprint(meetings)
    print(f"Total meetings scraped: {len(meetings)}")
