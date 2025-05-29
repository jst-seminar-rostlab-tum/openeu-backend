import logging
from datetime import date, datetime, timedelta
from typing import Any, Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup, Tag
from pydantic import BaseModel

from app.core.supabase_client import supabase
from app.data_sources.scraper_base import ScraperBase, ScraperResult

logger = logging.getLogger(__name__)

BASE_URL_TEMPLATE = (
    "https://www.europarl.europa.eu/plenary/en/meetings-search.html?isSubmitted=true&dateFrom={date}"
    "&townCode=&loadingSubType=false&meetingTypeCode=&retention=TODAY&page={page}"
)
EVENTS_TABLE_NAME = "ep_meetings"


class EPMeetingEntry(BaseModel):
    datetime: str
    title: Optional[str]
    subtitles: Optional[str]
    place: Optional[str]
    embedding_input: Optional[str]


class EPMeetingCalendarScraper(ScraperBase):
    """
    Scraper for all Meetings of the EP.
    """

    def __init__(
        self,
        start_date: date,
        end_date: date,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        """Initialize the scraper."""
        super().__init__(EVENTS_TABLE_NAME, max_retries, retry_delay)
        self.start_date = start_date
        self.end_date = end_date
        self.events: list[dict[str, Any]] = []
        self.session = requests.Session()

    def scrape_once(self, last_entry, **args) -> ScraperResult:
        """
        Scrape all Meetings of the EP.
        """

        current_date = self.start_date

        while current_date <= self.end_date:
            date_str = quote(current_date.strftime("%d/%m/%Y"))
            page_number = 0
            logger.info(f" Scraping meetings for date {current_date.strftime('%d-%m-%Y')}")
            while True:
                full_url = BASE_URL_TEMPLATE.format(date=date_str, page=page_number)
                page_soup = self._fetch_page_process_page(full_url)
                if page_soup is None:
                    break
                page_number += 1

            current_date += timedelta(days=1)
        return ScraperResult(True, last_entry=None)

    def delete_entries_in_range(self) -> None:
        """
        Deletes all entries in the target table within the given datetime range.
        """
        date_from = self.start_date.isoformat()
        date_to = (self.end_date + timedelta(days=1)).isoformat()  # end of the last day
        try:
            (((supabase.table(self.table_name).delete().gte("datetime", date_from)).lte("datetime", date_to)).execute())
            logger.info(f"Deleted entries from '{self.table_name}' between {date_from} and {date_to}")
        except Exception as e:
            logger.error(f"Failed to delete entries in Supabase: {e}")

    def _fetch_page_process_page(self, full_url: str) -> Optional[BeautifulSoup]:
        try:
            response = requests.get(full_url, timeout=60)
            if response.status_code != 200:
                logger.error(f"Non-200 response ({response.status_code}) for URL {full_url}")
                return None
        except Exception as e:
            logger.error(f"Request failed for URL {full_url}: {e}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        error_message = soup.find("div", class_="message_error")
        if error_message and "No result" in error_message.get_text(strip=True):
            logger.info(f" No results found on page: {full_url}")
            return None
        self._extract_meetings(soup)
        return soup

    def _extract_meetings(self, soup: BeautifulSoup) -> None:
        meetings_container = soup.find("div", class_="listcontent")

        if not isinstance(meetings_container, Tag):
            return

        meetings = meetings_container.find_all("div", class_="notice")

        batch = []

        for meeting in meetings:
            if not isinstance(meeting, Tag):
                continue

            title_tag = meeting.find("p", class_="title")

            title = title_tag.getText(strip=True) if title_tag else None

            session_tag = meeting.find("div", class_="session")

            if not isinstance(session_tag, Tag):
                continue

            subtitles_tag = session_tag.find("div", class_="subtitles")
            subtitles = subtitles_tag.get_text(strip=True) if subtitles_tag else None

            info_tag = session_tag.find("div", class_="info")

            if not isinstance(info_tag, Tag):
                continue

            date_tag = info_tag.find("p", class_="date")
            hour_tag = info_tag.find("p", class_="hour")
            place_tag = info_tag.find("p", class_="place")

            if not (isinstance(date_tag, Tag) and isinstance(hour_tag, Tag) and isinstance(place_tag, Tag)):
                continue

            date = date_tag.get_text(strip=True)
            hour = hour_tag.get_text(strip=True)
            place = place_tag.get_text(strip=True)

            try:
                datetime_obj = datetime.strptime(f"{date} {hour}", "%d-%m-%Y %H:%M")
            except ValueError:
                logger.warning(f"Failed to parse datetime from date='{date}' and hour='{hour}'")
                continue

            embedding_input = f"{title} {datetime_obj.isoformat()} {place or ''} {subtitles or ''}".strip()
            batch.append(
                EPMeetingEntry(
                    datetime=datetime_obj.isoformat(),
                    title=title,
                    subtitles=subtitles,
                    place=place,
                    embedding_input=embedding_input,
                ).model_dump()
            )

        if batch:
            self.store_entry(batch, embedd_entries=True)
        else:
            logger.info("No meetings found on this page")


def run_scraper(start_date: date, end_date: date):
    """
    Get EP Meetings with date range filtering.

    Args:
        start_date: Start date for filtering events
        end_date: End date for filtering events
    """
    scraper = EPMeetingCalendarScraper(start_date=start_date, end_date=end_date)
    scraper.delete_entries_in_range()
    scraper.scrape()


if __name__ == "__main__":
    # Example usage
    # start_date = date(2025, 7, 1)
    # end_date = date(2025, 7, 20)
    run_scraper(date(2025, 6, 5), date(2025, 6, 7))
