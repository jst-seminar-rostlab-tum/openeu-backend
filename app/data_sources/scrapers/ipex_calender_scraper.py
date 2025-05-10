from typing import List, Dict, Any, Optional
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# from app.core.supabase_client import supabase

# Constants
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


class IPEXEvent(BaseModel):
    """
    Model representing an event from the IPEX calendar.
    Contains all relevant information about the event.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="identifier")  # Unique identifier for the event
    title: str  # Event title
    event_type: str  # Type of the event (e.g., "Meeting", "Conference")

    # Date fields - different events have different date formats
    start_date: Optional[str] = None  # Start date of the event
    end_date: Optional[str] = None  # End date of the event
    single_date: Optional[str] = (
        None  # Used when event has a single date (not start/end)
    )
    event_time: Optional[str] = None  # Time of the event (e.g., "14:30")
    registration_deadline: Optional[str] = None  # Deadline for registration if provided

    # Location and organization fields
    meeting_location: Optional[str] = None  # Location where the event takes place
    organizers: Optional[str] = None  # Event organizers

    # Tags
    tags: Optional[List[str]] = None  # Tags/keywords shown as buttons on the event page


class IPEXCalendarScraper:
    """
    Scraper for calendar events from the IPEX website using Selenium.
    """

    def __init__(self):
        """Initialize the scraper with Selenium WebDriver."""
        self.events = []
        self.driver = self._setup_driver()

    def _setup_driver(self) -> webdriver.Chrome:
        """
        Set up and configure the Chrome WebDriver.

        Returns:
            Configured Chrome WebDriver instance
        """
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(f"user-agent={HEADERS['User-Agent']}")

        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)

    def scrape(self):
        """
        Scrape the calendar events from the IPEX website.
        """
        try:
            # Load the page
            self.driver.get(IPEX_CALENDAR_URL)

            # Wait for the event cards to be loaded
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".ipx-card-list"))
            )

            # Get all event cards
            event_cards = self.driver.find_elements(
                By.CSS_SELECTOR, ".ipx-card-content"
            )

            for card in event_cards:
                try:
                    # Extract event details
                    title = card.find_element(By.CSS_SELECTOR, "h3.ipx-card-title").text
                    description = card.find_element(
                        By.CSS_SELECTOR, "p.ipx-card-description"
                    ).text
                    location = card.find_element(
                        By.CSS_SELECTOR, ".ipx-card-footer span:last-child"
                    ).text
                    tags = [
                        tag.text
                        for tag in card.find_elements(
                            By.CSS_SELECTOR, ".badge.badge-home"
                        )
                    ]

                    # Extract event ID from the href attribute
                    event_url = card.get_attribute("href")
                    event_id = event_url.split("/")[-2] if event_url else None

                    # Parse date information
                    date_info = (
                        self._parse_date_info(description) if description else {}
                    )

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
                    print(f"Error processing event card: {e}")
                    continue

            # Save events to JSON file
            self._save_events()

        finally:
            self.driver.quit()

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


def run_scraper():
    """Run the IPEX calendar scraper."""
    scraper = IPEXCalendarScraper()
    scraper.scrape()


if __name__ == "__main__":
    run_scraper()
