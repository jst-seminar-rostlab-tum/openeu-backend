import json
import logging
import re
from datetime import date
from typing import Optional

import requests
from pydantic import BaseModel

from app.core.deepl_translator import translator
from app.core.supabase_client import supabase
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
    title: str
    type: str
    date: date
    location: str
    url: str


class AustrianParliamentAPI:
    """Client for retrieving data from the Austrian Parliament API."""

    def __init__(self):
        """Initialize the API client."""
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

    def get_meetings(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> list[AustrianParliamentMeeting]:
        """Retrieve meetings from the Austrian Parliament API.

        Args:
            start_date: Optional start date for filtering meetings
            end_date: Optional end date for filtering meetings

        Returns:
            List of AustrianParliamentMeeting objects
        """
        logger.info("Retrieving meetings from Austrian Parliament API")

        # Prepare request parameters
        params: dict[str, str] = {"js": "eval", "showAll": "true", "export": "true"}

        # Prepare request body
        body: dict[str, list[Optional[str]]] = {"DATERANGE": [None, None]}

        # Add date range if specified
        if start_date or end_date:

            if start_date:
                # Format start date with T22:00:00.000Z suffix as required by the API
                start_date_str = f"{start_date.isoformat()}T22:00:00.000Z"
                body["DATERANGE"][0] = start_date_str
                logger.info(f"Using start date: {start_date_str}")

            if end_date:
                # Format end date with T23:59:59.999Z suffix as required by the API
                end_date_str = f"{end_date.isoformat()}T23:59:59.999Z"
                body["DATERANGE"][1] = end_date_str
                logger.info(f"Using end date: {end_date_str}")

        try:
            # Make request to API
            response = self.session.post(PARLIAMENT_API_URL, params=params, json=body)
            response.raise_for_status()

            # Parse response
            meetings = self._parse_meetings(response.text)

            # Store meetings in Supabase
            self._store_meetings(meetings)

            logger.info(f"Successfully retrieved {len(meetings)} meetings")
            return meetings

        except requests.RequestException as e:
            logger.error(f"Network error: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return []

    def _parse_meetings(self, response_text: str) -> list[AustrianParliamentMeeting]:
        """Parse the API response into AustrianParliamentMeeting objects.

        Args:
            response_text: Raw API response text
            
        Returns:
            List of AustrianParliamentMeeting objects
        """
        logger.info("Parsing response from Austrian Parliament API")

        meetings: list[AustrianParliamentMeeting] = []

        try:
            # Try to parse the JSON-like response
            # First find the data row array in the response
            response_json = json.loads(response_text)

            if not isinstance(response_json, dict) or "rows" not in response_json:
                logger.error("Invalid response format: 'rows' field not found")
                return []

            meetings_data = response_json.get("rows", [])

            if not meetings_data:
                logger.info("No meetings found in the response")
                return []
                
            logger.info(f"Found {len(meetings_data)} meetings in the response")
            
            # Process each meeting
            for i, meeting_data in enumerate(meetings_data):
                # Skip if it's a "Führung Parlament" event
                if "Führung Parlament" in meeting_data:
                    continue
            
                if len(meeting_data) >= 9:
                    try:
                        # Extract required fields
                        date_str = meeting_data[0]
                        title = meeting_data[3]
                        type_str = meeting_data[5]
                        location = meeting_data[8]
                        url_path = meeting_data[4]
                        
                        # Clean up the title
                        title = self._clean_and_translate_title(title)
                        
                        # Parse date from DD.MM.YYYY format
                        day, month, year = map(int, date_str.split("."))
                        meeting_date = date(year, month, day)
                        
                        # Construct full URL
                        url = BASE_URL + url_path if url_path else ""
                        
                        meetings.append(
                            AustrianParliamentMeeting(
                                title=title,
                                type=type_str,
                                date=meeting_date,
                                location=location,
                                url=url
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

    def _clean_and_translate_title(self, title: str) -> str:
        """Clean up the meeting title.
        
        Args:
            title: Raw meeting title
            
        Returns:
            Cleaned meeting title
        """
        if not title:
            return ""
            
        # Replace HTML non-breaking space entities with regular spaces
        title = title.replace("&nbsp;", " ")
        
        # Remove leading dot and space (e.g., ". Sitzung")
        title = re.sub(r'^(\. )', '', title)
        
        # Remove any extra whitespace
        title = " ".join(title.split())
        
        # Translate the title using DeepLTranslator
        translation_result = self.translator.translate(title)
        
        return translation_result.text

    def _store_meetings(self, meetings: list[AustrianParliamentMeeting]) -> None:
        """Store meetings in Supabase database.

        Args:
            meetings: List of AustrianParliamentMeeting objects to store
        """
        if not meetings:
            logger.info("No meetings to store")
            return

        try:
            # Convert meetings to dict for database storage
            meetings_data = [meeting.model_dump() for meeting in meetings]

            # Store in Supabase
            supabase.table(MEETINGS_TABLE_NAME).insert(
                meetings_data,
                upsert=True,
            ).execute()
            logger.info(f"Successfully stored {len(meetings)} meetings in Supabase")
        except Exception as e:
            logger.error(f"Error storing meetings in Supabase: {e}")


def run_client(start_date: Optional[date] = None, end_date: Optional[date] = None):
    """
    Run the Austrian Parliament API client with optional date range filtering.

    Args:
        start_date: Optional start date for filtering meetings
        end_date: Optional end date for filtering meetings
    """
    api = AustrianParliamentAPI()
    api.get_meetings(start_date=start_date, end_date=end_date)


if __name__ == "__main__":
    # Example usage
    run_client(start_date=date(2025, 1, 1))
    # run_client()
