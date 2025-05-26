import json
import logging
from datetime import date, timedelta
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from pydantic import BaseModel

from app.core.deepl_translator import translator
from app.data_sources.scraper_base import ScraperBase, ScraperResult
from app.data_sources.translator.translator import DeepLTranslator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# Base URL for the Belgian Parliament
BASE_URL = "https://www.vlaamsparlement.be"
MEETINGS_URL = f"{BASE_URL}/nl/parlementair-werk/vergaderingen-en-verslagen"


class BelgianParliamentMeeting(BaseModel):
    """Model representing a meeting from the Belgian Parliament."""
    title: str
    title_en: str
    description: str
    description_en: str
    meeting_date: date
    location: str
    meeting_url: str


class BelgianParliamentScraper(ScraperBase):
    """Scraper for retrieving data from the Belgian Parliament website."""

    def __init__(self, start_date: Optional[date] = None, end_date: Optional[date] = None):
        """Initialize the scraper.
        
        Args:
            start_date: Optional start date for filtering meetings
            end_date: Optional end date for filtering meetings
        """
        super().__init__(table_name="belgian_parliament_meetings")
        self.translator = DeepLTranslator(translator)
        self.start_date = start_date or date.today()
        self.end_date = end_date or self.start_date
        self.current_date = self.start_date

    def scrape_once(self, last_entry: Optional[BelgianParliamentMeeting], *args) -> ScraperResult:
        """Run a single scraping attempt.

        Args:
            last_entry: The last successfully scraped entry
            *args: Additional arguments (not used)

        Returns:
            ScraperResult object
        """
        try:
            # If we have a last_entry, start from the day after its date
            if last_entry and last_entry.meeting_date:
                current_date = last_entry.meeting_date + timedelta(days=1)
                if current_date > self.end_date:
                    return ScraperResult(success=True, last_entry=last_entry)
            else:
                current_date = self.start_date

            all_meetings = []

            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()

                # Iterate through each day in the date range
                while current_date <= self.end_date:
                    try:
                        # Construct URL for the specific day
                        day_url = f"{MEETINGS_URL}?period={current_date.isoformat()}&view=day"
                        logger.info(f"Scraping meetings for {current_date.isoformat()}")
                        
                        # Update current_date for this iteration
                        self.current_date = current_date

                        # Navigate to the page
                        page.goto(day_url)
                        
                        # Wait for the content to load
                        page.wait_for_selector('.meeting-card', timeout=10000)

                        # Get the page content
                        content = page.content()
                        
                        # Parse the HTML content
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Find all meeting entries for this day
                        meeting_entries = soup.find_all('article', class_='meeting-card')
                        
                        for entry in meeting_entries:
                            try:
                                # Extract meeting information
                                meeting = self._extract_meeting_info(entry, page)
                                all_meetings.append(meeting)
                                
                            except Exception as e:
                                logger.warning(f"Error processing meeting entry: {e}")
                                continue

                    except Exception as e:
                        logger.error(f"Error scraping day {current_date}: {e}")
                        return ScraperResult(success=False, error=e, last_entry=last_entry)

                    # Move to next day
                    current_date += timedelta(days=1)

                # Close browser
                browser.close()

                # Store meetings to file
                self._store_meetings_to_file(all_meetings)
                
                return ScraperResult(success=True, last_entry=all_meetings[-1] if all_meetings else last_entry)

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return ScraperResult(success=False, error=e, last_entry=last_entry)

    def _extract_meeting_info(self, entry: BeautifulSoup, page) -> BelgianParliamentMeeting:
        """Extract meeting information from a BeautifulSoup entry.

        Args:
            entry: BeautifulSoup object containing meeting information
            page: Playwright page object for navigating to detail pages

        Returns:
            BelgianParliamentMeeting object
        """
        # Extract title
        title = entry.find('h4', class_='card__title').text.strip()
        title_en = self.translator.translate(title).text

        # Get the URL first as we'll need it for the full description
        url_path = entry.find('ul', class_='card__link-list').find('li').find('a')['href']
        meeting_url = BASE_URL + url_path if url_path.startswith('/') else url_path

        # First check if there's a description on the main page
        description_div = entry.find('div', class_='card__description')
        if description_div:
            # Get h3 text if present
            h3 = description_div.find('h3')
            h3_text = h3.get_text(strip=True) if h3 else ""
            
            # Get paragraph text
            p_text = description_div.find('p').get_text(strip=True) if description_div.find('p') else ""
            
            # Combine h3 and p text with colon if h3 exists
            description = f"{h3_text}: {p_text}" if h3_text else p_text
            
            # Only navigate to detail page if the description ends with "..." -> description is truncated
            if description.endswith("..."):
                # Navigate to the detail page to get full description
                page.goto(meeting_url)
                page.wait_for_selector('.card__description', timeout=10000)
                detail_content = page.content()
                detail_soup = BeautifulSoup(detail_content, 'html.parser')
                
                # Extract full description
                description_div = detail_soup.find('div', class_='card__description')
                if description_div:
                    # Get h3 text if present
                    h3 = description_div.find('h3')
                    h3_text = h3.get_text(strip=True) if h3 else ""
                    
                    # Get paragraph text
                    p_text = description_div.find('p').get_text(strip=True) if description_div.find('p') else ""
                    
                    # Combine h3 and p text with colon if h3 exists
                    description = f"{h3_text}: {p_text}" if h3_text else p_text
        else:
            description = ""
        
        description_en = self.translator.translate(description).text if description else ""

        # Extract date and location
        date_location = entry.find('div', class_='card__date').text.strip()
        # Split on " - " to separate time and location
        location = date_location.split(" - ", 1)[1]

        return BelgianParliamentMeeting(
            title=title,
            title_en=title_en,
            description=description,
            description_en=description_en,
            meeting_date=self.current_date,
            location=location,
            meeting_url=meeting_url
        )

    def _store_meetings_to_file(self, meetings: list[BelgianParliamentMeeting]) -> None:
        """Store meetings to a JSON file.

        Args:
            meetings: List of BelgianParliamentMeeting objects to store
        """
        if not meetings:
            logger.info("No meetings to store")
            return

        try:
            # Create data directory if it doesn't exist
            data_dir = Path("data")
            data_dir.mkdir(exist_ok=True)

            # Convert meetings to dict for JSON serialization
            meetings_data = [meeting.model_dump() for meeting in meetings]

            # Write to file
            output_file = data_dir / "belgian_parliament_meetings.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(meetings_data, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"Successfully stored {len(meetings)} meetings to {output_file}")

        except Exception as e:
            logger.error(f"Error storing meetings to file: {e}")


def run_scraper(start_date: Optional[date] = None, end_date: Optional[date] = None):
    """
    Run the Belgian Parliament scraper with optional date range filtering.

    Args:
        start_date: Optional start date for filtering meetings
        end_date: Optional end date for filtering meetings
    """
    scraper = BelgianParliamentScraper(start_date=start_date, end_date=end_date)
    result = scraper.scrape()
    return result


if __name__ == "__main__":
    # Example usage
    run_scraper(start_date=date(2025, 5, 13))
