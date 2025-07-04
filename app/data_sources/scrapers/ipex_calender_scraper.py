import json
import logging
from datetime import date
import multiprocessing
from typing import Any, Optional

import requests
from pydantic import BaseModel, ConfigDict, Field

from app.data_sources.scraper_base import ScraperBase, ScraperResult

# Endpoint for calendar events
IPEX_BASE_URL = "https://ipex.eu/IPEXL-WEB/api/search/event?appLng=EN"
EVENTS_TABLE_NAME = "ipex_events"


logger = logging.getLogger(__name__)


class IPEXEvent(BaseModel):
    """
    Model representing an event from the IPEX calendar.
    Contains all relevant information about the event.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="identifier")  # Unique identifier for the event
    title: str  # Event title
    start_date: Optional[str] = None  # Start date of the event
    end_date: Optional[str] = None  # End date of the event
    meeting_location: Optional[str] = None  # Location where the event takes place
    tags: Optional[list[str]] = None  # Tags/keywords from shared labels
    embedding_input: str


class IPEXCalendarAPIScraper(ScraperBase):
    """
    Scraper for calendar events from the IPEX API using POST requests.
    """

    def __init__(
        self,
        stop_event: multiprocessing.synchronize.Event,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        """Initialize the scraper."""
        super().__init__(EVENTS_TABLE_NAME, stop_event, max_retries, retry_delay)
        self.events: list[dict[str, Any]] = []
        self.start_date = start_date
        self.end_date = end_date
        self.session = requests.Session()

        # Configure Request headers
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
                      (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
            }
        )

    def _build_request_payload(self, page_number: int, start_date, end_date) -> dict[str, Any]:
        """
        Build the POST request payload for fetching events.

        Args:
            page_number: The page number to fetch

        Returns:
            Dictionary containing the request payload
        """
        payload: dict[str, Any] = {
            "pageNumber": page_number,
            "filters": {"type": ["calendarevent"]},
            "sort": {"startDate": "DESC"},
        }

        # Add date range filter if provided
        if start_date and end_date:
            date_range = [
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
            ]
            payload["filters"]["startDateByDateRange"] = date_range

        return payload

    def _parse_event(self, event_data: dict[str, Any]) -> Optional[IPEXEvent]:
        """
        Parse a single event from the API response.

        Args:
            event_data: Raw event data from API response

        Returns:
            Parsed IPEXEvent object or None if parsing fails
        """
        try:
            source_map = event_data.get("sourceAsMap", {})
            fields = event_data.get("fields", {})

            # Extract event ID from link field
            link_field = fields.get("link", {})
            link_value = link_field.get("value", "")
            event_id = link_value.split("/")[-1] if link_value else ""

            # Extract title
            titles = source_map.get("titles", [])
            title = ""
            if titles and len(titles) > 0:
                title = titles[0].get("message", "")

            # Extract dates and remove time component
            start_date = source_map.get("startDate")
            if start_date:
                start_date = start_date.split(" ")[0]  # Keep only date part
                start_date = date.fromisoformat(start_date)

            end_date = source_map.get("endDate")
            if end_date:
                end_date = end_date.split(" ")[0]  # Keep only date part
                end_date = date.fromisoformat(end_date)

            # Extract location
            address = source_map.get("address")

            # Extract tags from shared labels
            shared_items = source_map.get("shared", [])
            tags = []
            for shared_item in shared_items:
                labels = shared_item.get("labels", [])
                for label in labels:
                    if label.get("language") == "EN":
                        tags.append(label.get("message", ""))

            location = address.strip()
            # Create embedding input
            embedding_input = f"{title} {location} {start_date} {end_date} {tags}"

            return IPEXEvent(
                identifier=event_id,
                title=title.strip() if title else "",
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
                meeting_location=location if location else None,
                tags=tags if tags else None,
                embedding_input=embedding_input,
            )

        except Exception as e:
            logger.error(f"Error parsing event: {e}")
            return None

    def scrape_once(self, last_entry, **args) -> ScraperResult:
        """
        Scrape all calendar events from IPEX using POST requests.
        """
        page_number = 1
        total_events_processed = 0

        logger.info("Starting IPEX calendar scraping via API...")

        if "start_date" not in args:
            logger.error("Missing parameter 'start_date'")
            return ScraperResult(False, error=Exception('Missing parameter "start_date"'))

        if "end_date" not in args:
            logger.error("Missing parameter 'end_date'")
            return ScraperResult(False, error=Exception('Missing parameter "end_date"'))

        start_date = args.get("start_date")
        end_date = args.get("end_date")
        while True:
            try:
                if self.stop_event.is_set():
                    return ScraperResult(
                        False, error=Exception("Stop event is set, stopping the spider."), last_entry=self.last_entry
                    )

                # Build request payload
                payload = self._build_request_payload(page_number, start_date, end_date)

                # Make POST request
                response = self.session.post(IPEX_BASE_URL, json=payload)
                response.raise_for_status()

                # Parse response
                data = response.json()
                hits = data.get("hits", {}).get("hits", [])

                # If no hits, we've reached the end
                if not hits:
                    logger.info(f"No more events found at page {page_number}")
                    break

                # Process events from this page
                events_on_page = 0
                for i, event_data in enumerate(hits):
                    if last_entry == event_data:
                        continue
                    logger.info(f"Processing event {i + 1}/{len(hits)} on page {page_number}")
                    parsed_event = self._parse_event(event_data)
                    if parsed_event:
                        result = self.store_entry(parsed_event.model_dump(), embedd_entries=True)
                        if result:
                            return result
                        last_entry = event_data
                        events_on_page += 1

                total_events_processed += events_on_page
                logger.info(f"Page {page_number}: Processed {events_on_page} events (Total: {total_events_processed})")

                # Move to next page
                page_number += 1

            except requests.RequestException as e:
                logger.error(f"Network error on page {page_number}: {e}")
                return ScraperResult(False, error=e, last_entry=self.last_entry)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error on page {page_number}: {e}")
                return ScraperResult(False, error=e, last_entry=self.last_entry)
            except Exception as e:
                logger.error(f"Unexpected error on page {page_number}: {e}")
                return ScraperResult(False, error=e, last_entry=self.last_entry)

        logger.info(f"Scraping completed. Total events: {len(self.events)}")

        # Store events in database
        return ScraperResult(True)


def run_scraper(
    stop_event: multiprocessing.synchronize.Event, start_date: Optional[date] = None, end_date: Optional[date] = None
) -> ScraperResult:
    """
    Run the IPEX calendar API scraper with optional date range filtering.

    Args:
        start_date: Optional start date for filtering events
        end_date: Optional end date for filtering events
    """
    scraper = IPEXCalendarAPIScraper(stop_event=stop_event)
    return scraper.scrape(start_date=start_date, end_date=end_date)


if __name__ == "__main__":
    # Example usage with date range
    start = date(2025, 5, 1)
    end = date(2025, 5, 31)
    run_scraper(start_date=start, end_date=end, stop_event=multiprocessing.Event())

    # Or run without date range to get all events
    # run_scraper()
