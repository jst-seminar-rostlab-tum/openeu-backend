import json
import logging
import re
from datetime import date
from typing import Any, Optional

import requests
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

# API endpoint
BASE_URL = "https://www.parlament.gv.at/"
PARLIAMENT_API_URL = "https://www.parlament.gv.at/Filter/api/filter/data/600"
MEETINGS_TABLE_NAME = "austrian_parliament_meetings"


class AustrianParliamentMeeting(BaseModel):
    """Model representing a meeting from the Austrian Parliament API."""
    id: str
    title: str
    title_de: str
    meeting_type: str
    meeting_date: str
    meeting_location: str
    meeting_url: str
    embedding_input: str


class AustrianParliamentScraper(ScraperBase):
    """Scraper for retrieving data from the Austrian Parliament API."""

    def __init__(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        """Initialize the scraper."""
        super().__init__(MEETINGS_TABLE_NAME, max_retries, retry_delay)
        self.start_date = start_date
        self.end_date = end_date
        self.session = requests.Session()
        self.translator = DeepLTranslator(translator)

        # Configure headers for request
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                      Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json",
            }
        )

    def _build_request_payload(self) -> dict[str, Any]:
        """Build the request payload for the API."""
        params: dict[str, str] = {"js": "eval", "showAll": "true", "export": "true"}
        body: dict[str, list[Optional[str]]] = {"DATERANGE": [None, None]}

        if self.start_date or self.end_date:
            if self.start_date:
                start_date_str = f"{self.start_date.isoformat()}T22:00:00.000Z"
                body["DATERANGE"][0] = start_date_str
                logger.info(f"Using start date: {start_date_str}")

            if self.end_date:
                end_date_str = f"{self.end_date.isoformat()}T23:59:59.999Z"
                body["DATERANGE"][1] = end_date_str
                logger.info(f"Using end date: {end_date_str}")

        return {"params": params, "body": body}

    def _parse_meetings(self, response_text: str) -> list[AustrianParliamentMeeting]:
        """Parse the API response into AustrianParliamentMeeting objects."""
        logger.info("Parsing response from Austrian Parliament API")
        meetings: list[AustrianParliamentMeeting] = []

        try:
            response_json = json.loads(response_text)
            if not isinstance(response_json, dict) or "rows" not in response_json:
                logger.error("Invalid response format: 'rows' field not found")
                return []

            meetings_data = response_json.get("rows", [])
            if not meetings_data:
                logger.info("No meetings found in the response")
                return []

            logger.info(f"Found {len(meetings_data)} meetings in the response")

            for i, meeting_data in enumerate(meetings_data):
                if any(
                    keyword in meeting_data
                    for keyword in [
                        "Führung Parlament",
                        "Führung",
                        "Guided Tour",
                        "Galeriebesuch Nationalrat",
                        "Photo Tour",
                    ]
                ):
                    continue

                if len(meeting_data) >= 9:
                    try:
                        date_str = meeting_data[0]
                        title = meeting_data[3]
                        meeting_type = meeting_data[5]
                        location = meeting_data[8]
                        url_path = meeting_data[4]

                        if not url_path:
                            logger.warning(f"No URL path found for meeting at index {i}")
                            continue

                        title_de, title_en = self._clean_and_translate_title(title)
                        day, month, year = map(int, date_str.split("."))
                        meeting_date = date(year, month, day).strftime("%Y-%m-%d")
                        url = BASE_URL + url_path
                        id = str(url_path.split("/")[-1])

                        # Create embedding input by concatenating the specified fields
                        embedding_input = f"{title_en} {meeting_type}"

                        meetings.append(
                            AustrianParliamentMeeting(
                                id=id,
                                title=title_en,
                                title_de=title_de,
                                meeting_type=meeting_type,
                                meeting_date=meeting_date,
                                meeting_location=location,
                                meeting_url=url,
                                embedding_input=embedding_input,
                            )
                        )
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing meeting at index {i}: {e}")
                        continue
                else:
                    logger.warning(f"Meeting data at index {i} has insufficient elements")

            return meetings

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return []

    def _clean_and_translate_title(self, title: str) -> tuple[str, str]:
        """Clean up and translate the meeting title."""
        if not title:
            return "", ""

        title = title.replace("&nbsp;", " ")
        title = re.sub(r"^(\. )", "", title)
        title = " ".join(title.split())
        translation_result = self.translator.translate(title)

        return title, translation_result.text

    def scrape_once(self, last_entry: Any, **args) -> ScraperResult:
        """Run a single scraping attempt."""
        logger.info("Starting Austrian Parliament scraping...")

        try:
            # Build request payload
            payload = self._build_request_payload()

            # Make request to API
            response = self.session.post(PARLIAMENT_API_URL, params=payload["params"], json=payload["body"], timeout=2)
            response.raise_for_status()

            # Parse meetings
            meetings = self._parse_meetings(response.text)

            # Store each meeting
            for meeting in meetings:
                self.store_entry(meeting.model_dump(), "id")

            logger.info(f"Successfully processed {len(meetings)} meetings")
            return ScraperResult(True)

        except requests.RequestException as e:
            logger.error(f"Network error: {e}")
            return ScraperResult(False, e, self.last_entry)
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return ScraperResult(False, e, self.last_entry)
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return ScraperResult(False, e, self.last_entry)


def run_scraper(start_date: Optional[date] = None, end_date: Optional[date] = None):
    """
    Run the Austrian Parliament scraper with optional date range filtering.

    Args:
        start_date: Optional start date for filtering meetings
        end_date: Optional end date for filtering meetings
    """
    scraper = AustrianParliamentScraper(start_date=start_date, end_date=end_date)
    scraper.scrape()


if __name__ == "__main__":
    # Example usage
    run_scraper(start_date=date(2025, 5, 20), end_date=date(2025, 5, 21))
    # run_scraper()
