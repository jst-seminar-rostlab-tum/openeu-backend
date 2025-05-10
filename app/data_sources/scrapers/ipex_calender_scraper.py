from typing import List, Dict, Any, Optional
import scrapy
from datetime import datetime, date
from pydantic import BaseModel, ConfigDict, Field
from scrapy.crawler import CrawlerProcess
from scrapy import Request
from urllib.parse import urlencode
import json
import os
import csv

from app.core.supabase_client import supabase

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

    id: str  # Unique identifier for the event
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

    # Additional metadata
    keywords: Optional[str] = None  # Keywords associated with the event
    tags: Optional[List[str]] = None  # Tags/keywords shown as buttons on the event page
