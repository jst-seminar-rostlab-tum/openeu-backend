import scrapy
from scrapy.crawler import CrawlerProcess
from typing import Generator, Optional, List
from datetime import date
from urllib.parse import urlencode
import re
from pydantic import BaseModel

"""
This file contains a Scrapy spider to scrape MEP meetings from the European Parliament website.
The file can be run as a standalone script to test the scraping functionality.
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

    def __init__(self, start_date, end_date, result_callback=None):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.base_url = "https://www.europarl.europa.eu/meps/en/search-meetings?"
        self.result_callback = result_callback
        self.meetings = []

    def start_requests(self):
        yield self.scrape_page(0)

    def scrape_page(self, page) -> scrapy.Request:
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

    def parse_search_results_page(self, response) -> Generator[scrapy.Request, None, None]:
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

    def parse_total_pages_num(self, response) -> int:
        """
        Parse the total number of pages from the search results.
        :param response: The response object from the search results page.
        :return: The total number of pages.
        """
        NUM_RESULTS_PER_PAGE = 10

        result_text = response.css(
            "#meetingSearchResultCounterText::text").get()
        # example text: "Showing 10 of 100 results"
        total_results = int(
            re.search(r'of (\d+)', result_text).group(1)) if result_text else 0
        total_pages = (total_results // NUM_RESULTS_PER_PAGE)
        return total_pages

    def parse_meeting(self, sel) -> MEPMeeting:
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
        meeting_date = sel.css("time::attr(datetime)").get()
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
# Main Function for Testing
# ------------------------------


if __name__ == "__main__":
    from pprint import pprint
    import datetime

    meetings = scrape_meetings(
        start_date=datetime.date(2025, 5, 15),
        end_date=datetime.date(2025, 5, 15
                               )
    )

    pprint(meetings)
    print(f"Total meetings scraped: {len(meetings)}")
