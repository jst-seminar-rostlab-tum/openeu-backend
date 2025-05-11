from typing import List, Dict, Any, Optional, Set
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field
import json
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
    ElementClickInterceptedException,
)

IPEX_CALENDAR_URL = "https://ipexl.europarl.europa.eu/IPEXL-WEB/calendar"
EVENTS_TABLE_NAME = "ipex_events"

# Request headers to mimic normal browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Cache-Control": "max-age=0",
    "X-Requested-With": "XMLHttpRequest",
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


class IPEXEvent(BaseModel):
    """
    Model representing an event from the IPEX calendar.
    Contains all relevant information about the event.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="identifier")  # Unique identifier for the event
    title: str  # Event title

    # Date fields - different events have different date formats
    start_date: Optional[str] = None  # Start date of the event
    end_date: Optional[str] = None  # End date of the event
    single_date: Optional[str] = (
        None  # Used when event has a single date (not start/end)
    )
    event_time: Optional[str] = None  # Time of the event (e.g., "14:30")

    meeting_location: Optional[str] = None  # Location where the event takes place

    tags: Optional[List[str]] = None  # Tags/keywords shown as buttons on the event page


class IPEXCalendarScraper:
    """
    Scraper for calendar events from the IPEX website using Selenium.
    """

    def __init__(self):
        """Initialize the scraper with Selenium WebDriver."""
        self.events = []
        self.processed_event_ids = set()  # Track already processed event IDs
        self.driver = self._setup_driver()
        self.last_event_count = (
            0  # Track number of events to detect when no new ones are loaded
        )

    def _setup_driver(self) -> webdriver.Chrome:
        """
        Set up and configure the Chrome WebDriver optimized for cloud/headless use.
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--window-size=1366,768")
        chrome_options.add_argument(f"user-agent={HEADERS['User-Agent']}")

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def scrape(self):
        """
        Scrape all calendar events from the IPEX website by loading more events
        until all are retrieved.
        """
        try:
            # Load the page
            self.driver.get(IPEX_CALENDAR_URL)

            # Wait for the initial event cards to be loaded
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ipx-card-list"))
            )

            # Keep track of consecutive attempts with no new events
            no_new_events_count = 0
            max_no_new_events = (
                3  # Stop after 3 consecutive attempts with no new events
            )

            while True:
                # Get the current count of processed events
                current_count = len(self.processed_event_ids)

                # Process visible events
                self._process_visible_events()

                # Check if we found new events
                if len(self.processed_event_ids) > current_count:
                    # Reset counter if we found new events
                    no_new_events_count = 0
                    logger.info(
                        f"Found {len(self.processed_event_ids) - current_count} new events"
                    )
                else:
                    # Increment counter if no new events were found
                    no_new_events_count += 1
                    logger.info(
                        f"No new events found. Attempt {no_new_events_count}/{max_no_new_events}"
                    )

                # Try to click "LOAD MORE" button
                if not self._click_load_more_button():
                    logger.info("No 'LOAD MORE' button found - reached the end")
                    break

                # Exit if we've had too many attempts with no new events
                if no_new_events_count >= max_no_new_events:
                    logger.info(
                        f"No new events after {max_no_new_events} attempts - stopping"
                    )
                    break

            logger.info(f"Total events scraped: {len(self.events)}")

            # Save events to JSON file
            self._save_events()

        finally:
            self.driver.quit()

    def _process_visible_events(self):
        """
        Process all currently visible event cards on the page.
        Only processes events that haven't been processed before.
        """
        # Get all event cards
        event_cards = self.driver.find_elements(By.CSS_SELECTOR, ".ipx-card-content")

        # Track how many new events we process in this batch
        new_events_count = 0

        for card in event_cards:
            try:
                # Extract event ID from the href attribute
                event_url = card.get_attribute("href")
                event_id = event_url.split("/")[-2] if event_url else None

                # Skip if we've already processed this event
                if not event_id or event_id in self.processed_event_ids:
                    continue

                # Add to processed set
                self.processed_event_ids.add(event_id)
                new_events_count += 1

                # Extract event details
                title = card.find_element(By.CSS_SELECTOR, "h3.ipx-card-title").text

                try:
                    description = card.find_element(
                        By.CSS_SELECTOR, "p.ipx-card-description"
                    ).text
                except NoSuchElementException:
                    description = ""

                # Extract location - handle possible missing elements
                try:
                    location = card.find_element(
                        By.CSS_SELECTOR, ".ipx-card-footer span:last-child"
                    ).text
                except NoSuchElementException:
                    location = None

                # Extract tags
                tags = [
                    tag.text
                    for tag in card.find_elements(By.CSS_SELECTOR, ".badge.badge-home")
                ]

                # Parse date information
                date_info = self._parse_date_info(description) if description else {}

                # Create event object
                event = IPEXEvent(
                    identifier=event_id,
                    title=title.strip() if title else "",
                    event_type="Meeting",
                    meeting_location=location.strip() if location else None,
                    tags=tags,
                    **date_info,
                )

                self.events.append(event.model_dump())

            except Exception as e:
                logger.error(f"Error processing event card: {e}")
                continue

        logger.info(f"Processed {new_events_count} new events in this batch")

    def _click_load_more_button(self) -> bool:
        """
        Scroll to the bottom of the page and click the "LOAD MORE" button if available.

        Returns:
            True if the button was clicked successfully, False otherwise
        """
        try:
            # Scroll down to the bottom to ensure the "LOAD MORE" button is in the viewport
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            # Try to find the "LOAD MORE" button
            load_more_button = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".btn-load"))
            )

            # Scroll directly to the button
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", load_more_button
            )

            # Try to click the button
            load_more_button.click()

            return True

        except (NoSuchElementException, TimeoutException):
            # No more "LOAD MORE" button found
            return False
        except ElementClickInterceptedException:
            # The button might be intercepted by another element
            try:
                # Try using JavaScript click as an alternative
                load_more_button = self.driver.find_element(
                    By.CSS_SELECTOR, ".loadMoreContainer button"
                )
                self.driver.execute_script("arguments[0].click();", load_more_button)
                return True
            except Exception as e:
                logger.error(f"Failed to click 'LOAD MORE' button: {e}")
                return False

    def _parse_date_info(self, date_str: str) -> Dict[str, Optional[str]]:
        """
        Parse the date string from the event description.

        Args:
            date_str: String containing date information

        Returns:
            Dictionary containing parsed date information
        """
        date_str = date_str.strip()

        # Handle different date formats
        if " - " in date_str:  # Single date with time
            date_part, time_part = date_str.split(" - ")
            return {"single_date": date_part.strip(), "event_time": time_part.strip()}
        elif "-" in date_str:  # Date range
            start, end = date_str.split("-")
            return {"start_date": start.strip(), "end_date": end.strip()}
        else:  # Single date
            return {"single_date": date_str.strip()}

    def _save_events(self):
        """Save scraped events to a JSON file."""
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, "ipex_events.json")
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(self.events, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(self.events)} events to {output_file}")


def run_scraper():
    """Run the IPEX calendar scraper."""
    scraper = IPEXCalendarScraper()
    scraper.scrape()


if __name__ == "__main__":
    run_scraper()
