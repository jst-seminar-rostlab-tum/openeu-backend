import asyncio
import calendar
import re
from datetime import date
from pprint import pprint
from typing import Optional, Tuple
from urllib.parse import urlencode

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

# from app.core.supabase_client import supabase
from pydantic import BaseModel

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


class MECSummitMinisterialMeeting(BaseModel):
    url: str
    title: str
    meeting_date: date
    meeting_end_date: Optional[date]
    category_abbr: Optional[str]


# ------------------------------
# Util Functions
# ------------------------------


def parse_meeting_dates(year_str: str, month_str: str, day_range_str: str) -> Tuple[date, Optional[date]]:
    """
    Parses meeting start and optional end dates from a year, month, and day range string.

    Args:
        year (str): The year as a 4-digit string.
        month (str): The month as a 2-digit string.
        day_range (str): A day or range like "3" or "30-2".

    Returns:
        Tuple[date, Optional[date]]: (start_date, end_date)
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


def test_parse_meeting_dates():
    # Case 1: Single day
    start, end = parse_meeting_dates("2024", "05", "3")
    assert start == date(2024, 5, 3)
    assert end is None

    # Case 2: Normal range within same month
    start, end = parse_meeting_dates("2024", "05", "3-5")
    assert start == date(2024, 5, 3)
    assert end == date(2024, 5, 5)

    # Case 3: Range spanning two months (e.g., May 31 – June 2)
    start, end = parse_meeting_dates("2024", "06", "31-2")
    assert start == date(2024, 5, 31)
    assert end == date(2024, 6, 2)

    # Case 4: Weirdly reversed but same month (should still parse correctly)
    start, end = parse_meeting_dates("2024", "05", "5-3")
    assert start == date(2024, 4, 5)
    assert end == date(2024, 5, 3)

    # Case 5: spanning 2 years
    start, end = parse_meeting_dates("2024", "01", "31-2")
    assert start == date(2023, 12, 31)
    assert end == date(2024, 1, 2)


# ------------------------------
# Scraping Logic
# ------------------------------


def get_largest_page_number(links: list[dict]) -> int:
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


async def scrape_meetings_by_page(start_date: date, end_date: date, page: int, crawler: AsyncWebCrawler):
    print(f"Scraping page {page} for meetings between {start_date} and {end_date}")
    found_meetings = []
    params = {
        "DateFrom": start_date.strftime("%Y/%m/%d"),
        "DateTo": end_date.strftime("%Y/%m/%d"),
        "category": "meeting",
        "page": page,
    }
    url = "https://www.consilium.europa.eu/en/meetings/calendar/" + "?" + urlencode(params)
    config = CrawlerRunConfig()
    result = await crawler.arun(url=url, crawler_config=config)
    internal_links = result.links.get("internal", [])
    links_to_meetings = [
        x for x in internal_links if x["href"].startswith("https://www.consilium.europa.eu/en/meetings/")
    ]

    # matches patterns like /meetings/agrifish/2024/05/3-5/
    meeting_url_pattern = re.compile(r"/meetings/([a-z0-9-]+)/(\d{4})/(\d{2})/([\d\-]+)/")

    for link in links_to_meetings:
        match = meeting_url_pattern.search(link["href"])
        if match:
            meeting_date, meeting_end_date = parse_meeting_dates(
                year_str=match.group(2),
                month_str=match.group(3),
                day_range_str=match.group(4),
            )

            found_meetings.append(
                MECSummitMinisterialMeeting(
                    url=link["href"],
                    title=link["text"],
                    meeting_date=meeting_date,
                    meeting_end_date=meeting_end_date,
                    category_abbr=match.group(1),
                )
            )

    largest_page = get_largest_page_number(links_to_meetings)

    return (found_meetings, largest_page)


async def scrape_meetings(start_date: date, end_date: date) -> list[MECSummitMinisterialMeeting]:
    found_meetings: list[MECSummitMinisterialMeeting] = []
    current_page = 1
    largest_known_page = 1

    async with AsyncWebCrawler() as crawler:
        while current_page <= largest_known_page:
            (meetings_on_page, largest_known_page) = await scrape_meetings_by_page(
                start_date=start_date,
                end_date=end_date,
                page=current_page,
                crawler=crawler,
            )
            found_meetings.extend(meetings_on_page)
            current_page += 1

    # Remove duplicates based on URL and title
    found_meetings = list({(meeting.url, meeting.title): meeting for meeting in found_meetings}.values())

    print(f"Found {len(found_meetings)} meetings.")
    return found_meetings


# ------------------------------
# Main Function for Testing
# ------------------------------

if __name__ == "__main__":

    async def main():
        meetings = await scrape_meetings(
            start_date=date(2025, 5, 17),
            end_date=date(2025, 6, 17),
        )
        pprint(meetings)

    asyncio.run(main())
