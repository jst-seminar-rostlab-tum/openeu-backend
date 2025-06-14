import logging
from datetime import date, timedelta
from typing import Any, Optional

from bs4 import BeautifulSoup, Tag
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
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
    id: str
    title: str
    title_en: str
    description: str
    description_en: str
    meeting_date: str
    location: str
    meeting_url: str
    embedding_input: str

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

    def scrape_once(self, last_entry: Any, **args: Any) -> ScraperResult:
        """Run a single scraping attempt.

        Args:
            last_entry: The last successfully scraped entry
            **args: Additional arguments (not used)

        Returns:
            ScraperResult object
        """
        try:
            # If we have a last_entry, start from the day after its date
            if last_entry and hasattr(last_entry, 'meeting_date') and last_entry.meeting_date:
                current_date = last_entry.meeting_date + timedelta(days=1)
                if current_date > self.end_date:
                    return ScraperResult(success=True, last_entry=last_entry)
            else:
                current_date = self.start_date

            with sync_playwright() as p:
                # Launch browser
                try:
                    browser = p.chromium.launch(headless=True)
                    page = browser.new_page()
                except Exception as e:
                    logger.error(f"Failed to launch browser: {e}")
                    return ScraperResult(success=False, error=e, last_entry=self.last_entry)

                # Iterate through each day in the date range
                while current_date <= self.end_date:
                    try:
                        # Construct URL for the specific day
                        day_url = f"{MEETINGS_URL}?period={current_date.isoformat()}&view=day"
                        logger.info(f"Scraping meetings for {current_date.isoformat()}")
                        
                        self.current_date = current_date

                        # Navigate to the page
                        try:
                            page.goto(day_url)
                        except Exception as e:
                            logger.error(f"Failed to navigate to {day_url}: {e}")
                            # Major error: abort scraping
                            return ScraperResult(success=False, error=e, last_entry=self.last_entry)

                        # Wait for the content to load, but skip if no meetings
                        try:
                            page.wait_for_selector('.meeting-card', timeout=10000)
                        except PlaywrightTimeoutError:
                            logger.info(f"No meetings found for {current_date.isoformat()}, skipping.")
                            current_date += timedelta(days=1)
                            continue

                        # Get the page content
                        content = page.content()
                        
                        # Parse the HTML content
                        soup = BeautifulSoup(content, 'html.parser')
                        
                        # Find all meeting entries for this day
                        meeting_entries = soup.find_all('article', class_='meeting-card')
                        
                        for entry in meeting_entries:
                            try:
                                # Ensure entry is a Tag object
                                if not isinstance(entry, Tag):
                                    continue
                                # Extract meeting information
                                meeting = self._extract_meeting_info(entry, page)
                                
                                # Store the meeting in the database
                                result = self.store_entry(meeting.model_dump())
                                if result:
                                    return result
                                
                                self.last_entry = meeting
                                
                            except Exception as e:
                                logger.warning(f"Error processing meeting entry: {e}")
                                continue

                    except Exception as e:
                        # Major error for the whole day: log and skip the day, or abort
                        logger.error(f"Error scraping day {current_date}: {e}")
                        # Abort scraping (uncomment to abort)
                        return ScraperResult(success=False, error=e, last_entry=self.last_entry)

                    # Move to next day
                    current_date += timedelta(days=1)

                # Close browser
                browser.close()
                
                return ScraperResult(success=True, last_entry=self.last_entry)

        except Exception as e:
            logger.error(f"Error during scraping: {e}")
            return ScraperResult(success=False, error=e, last_entry=last_entry)

    def _extract_meeting_info(self, entry: Tag, page) -> BelgianParliamentMeeting:
        """Extract meeting information from a BeautifulSoup Tag entry.

        Args:
            entry: BeautifulSoup Tag object containing meeting information
            page: Playwright page object for navigating to detail pages

        Returns:
            BelgianParliamentMeeting object
        """
        # Extract title
        title_element = entry.find('h4', class_='card__title')
        if not title_element:
            raise ValueError("Title element not found")
        title = title_element.text.strip()
        title_en = ""
        try:
            translation_result = self.translator.translate(title)
            title_en = translation_result.text
        except Exception as e:
            logger.warning(f"Translation failed for title '{title}': {e}. Using Belgian title as English title.")
            title_en = title

        # Get the URL first as we possibly need it for the full description
        link_list = entry.find('ul', class_='card__link-list')
        if not link_list or not isinstance(link_list, Tag):
            raise ValueError("Link list not found")
        link_element = link_list.find('li')
        if not link_element or not isinstance(link_element, Tag):
            raise ValueError("Link element not found")
        anchor = link_element.find('a')
        if not anchor or not isinstance(anchor, Tag):
            raise ValueError("Anchor element or href not found")
        url_path = str(anchor['href'])
        meeting_url = BASE_URL + url_path if url_path.startswith('/') else url_path

        # get id from url
        meeting_id = str(url_path.split('/')[-1])

        # First check if there's a description on the main page
        description_div = entry.find('div', class_='card__description')
        if description_div and isinstance(description_div, Tag):
            # Get h3 text if present
            h3 = description_div.find('h3')
            h3_text = h3.get_text(strip=True) if h3 else ""
            
            # Get paragraph text
            p_element = description_div.find('p')
            p_text = p_element.get_text(strip=True) if p_element else ""
            
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
                if description_div and isinstance(description_div, Tag):
                    # Get h3 text if present
                    h3 = description_div.find('h3')
                    h3_text = h3.get_text(strip=True) if h3 else ""
                    
                    # Get paragraph text
                    p_element = description_div.find('p')
                    p_text = p_element.get_text(strip=True) if p_element else ""
                    
                    # Combine h3 and p text with colon if h3 exists
                    description = f"{h3_text}: {p_text}" if h3_text else p_text
        else:
            description = ""
    
        description_en = ""
        if description:
            try:
                translation_result = self.translator.translate(description)
                description_en = translation_result.text
            except Exception as e:
                logger.warning(f"Translation failed for description '{description}': {e}. \
                               Using Belgian description as English description.")
                description_en = description


        # Extract date and location
        date_element = entry.find('div', class_='card__date')
        if not date_element:
            raise ValueError("Date element not found")
        date_location = date_element.text.strip()
        # Split on " - " to separate time and location
        location = date_location.split(" - ", 1)[1]

        meeting_date = self.current_date.strftime("%Y-%m-%d")

        # create embedding input
        embedding_input = f"{title_en} {description_en} {meeting_date} {location}"

        return BelgianParliamentMeeting(
            id=meeting_id,
            title=title,
            title_en=title_en,
            description=description,
            description_en=description_en,
            meeting_date=meeting_date,
            location=location,
            meeting_url=meeting_url,
            embedding_input=embedding_input
        )


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
