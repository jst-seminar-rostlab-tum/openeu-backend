import json
import logging
import re
from datetime import date
from pathlib import Path
from typing import Optional

import requests

from app.models.meeting import Meeting

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)

logger = logging.getLogger(__name__)

# API endpoint
PARLIAMENT_API_URL = "https://www.parlament.gv.at/Filter/api/filter/data/600"


class AustrianParliamentAPI:
    """Client for retrieving data from the Austrian Parliament API."""

    def __init__(self, cache_dir: str = "data"):
        """Initialize the API client.

        Args:
            cache_dir: Directory where JSON data will be stored
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.session = requests.Session()

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
    ) -> list[Meeting]:
        """Retrieve meetings from the Austrian Parliament API.

        Args:
            start_date: Optional start date for filtering meetings
            end_date: Optional end date for filtering meetings

        Returns:
            List of Meeting objects
        """
        logger.info("Retrieving meetings from Austrian Parliament API")

        # Prepare request parameters
        params: dict[str, str] = {"js": "eval", "showAll": "true", "export": "true"}

        # Prepare request body
        body: dict[str, list[str]] = {"DATERANGE": [None, None]}

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

            # Save to JSON file
            self._save_to_json(meetings)

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

    def _parse_meetings(self, response_text: str) -> list[Meeting]:
        """Parse the API response into Meeting objects.

        Args:
            response_text: Raw API response text
            
        Returns:
            List of Meeting objects
        """
        logger.info("Parsing response from Austrian Parliament API")

        meetings: list[Meeting] = []

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
                if len(meeting_data) >= 4:
                    try:
                        # Extract date (first element) and title (fourth element)
                        date_str = meeting_data[0]
                        title = meeting_data[3]
                        
                        # Clean up the title
                        title = self._clean_title(title)
                        
                        # Parse date from DD.MM.YYYY format
                        day, month, year = map(int, date_str.split("."))
                        meeting_date = date(year, month, day)
                        
                        meetings.append(Meeting(date=meeting_date, name=title, tags=[]))
                    except (ValueError, IndexError) as e:
                        logger.warning(f"Error parsing meeting at index {i}: {e}")
                        continue
                else:
                    logger.warning(f"Meeting data at index {i} has insufficient elements")
            
            return meetings
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")

        except Exception as e:
            logger.error(f"Error parsing response: {e}")
            return []

    def _clean_title(self, title: str) -> str:
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
        
        return title

    def _save_to_json(self, meetings: list[Meeting]) -> None:
        """Save meetings to a JSON file.

        Args:
            meetings: List of Meeting objects to save
        """
        if not meetings:
            logger.info("No meetings to save to JSON")
            return

        try:
            # Convert meetings to dict for JSON serialization
            meetings_data = [meeting.model_dump() for meeting in meetings]

            # Convert date objects to strings for JSON serialization
            for meeting_data in meetings_data:
                if isinstance(meeting_data["date"], date):
                    meeting_data["date"] = meeting_data["date"].isoformat()

            # Save to file
            output_path = self.cache_dir / "austrian_parliament_meetings.json"
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(meetings_data, f, ensure_ascii=False, indent=2)

            logger.info(f"Saved {len(meetings)} meetings to {output_path}")
        except Exception as e:
            logger.error(f"Error saving meetings to JSON: {e}")


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
    run_client(start_date=date(2020, 1, 1))
    # run_client()
