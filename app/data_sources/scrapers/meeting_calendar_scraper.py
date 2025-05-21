import logging
from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from app.core.supabase_client import supabase

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

BASE_URL_TEMPLATE = (
    "https://www.europarl.europa.eu/plenary/en/meetings-search.html?isSubmitted=true&dateFrom={date}"
    "&townCode=&loadingSubType=false&meetingTypeCode=&retention=TODAY&page={page}"
)


def scrape_meeting_calendar(start_date: str, end_date: str) -> None:
    start_date_dated = datetime.strptime(start_date, "%d-%m-%Y")
    end_date_dated = datetime.strptime(end_date, "%d-%m-%Y")

    current_date = start_date_dated

    while current_date <= end_date_dated:
        date_str = quote(current_date.strftime("%d/%m/%Y"))
        page_number = 0
        logging.info(f"Scraping meetings for date {current_date.strftime('%d-%m-%Y')}")
        while True:
            full_url = BASE_URL_TEMPLATE.format(date=date_str, page=page_number)
            page_soup = fetch_and_process_page(full_url)
            if page_soup is None:
                break
            page_number += 1

        current_date += timedelta(days=1)


def fetch_and_process_page(full_url: str) -> Optional[BeautifulSoup]:
    try:
        response = requests.get(full_url, timeout=60)
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for URL {full_url}: {e}")
        return None

    if response.status_code != 200:
        logging.error(f"Non-200 response ({response.status_code}) for URL {full_url}")
        return None
    soup = BeautifulSoup(response.text, "html.parser")
    error_message = soup.find("div", class_="message_error")
    if error_message and "No result" in error_message.get_text(strip=True):
        logging.info(f"No results found on page: {full_url}")
        return None

    extract_meeting_info(soup)
    return soup


def extract_meeting_info(soup: BeautifulSoup) -> None:
    meetings_container = soup.find("div", class_="listcontent")
    meetings = []
    if meetings_container is not None:
        meetings = meetings_container.find_all("div", class_="notice")  # type: ignore

    batch = []

    for meeting in meetings:
        title_tag = meeting.find("p", class_="title")

        title = title_tag.getText(strip=True) if title_tag else None

        session_tag = meeting.find("div", class_="session")

        if not session_tag:
            continue

        subtitles_tag = session_tag.find("div", class_="subtitles")
        subtitles = subtitles_tag.get_text(strip=True) if subtitles_tag else None

        info_tag = session_tag.find("div", class_="info")

        if not info_tag:
            continue

        date_tag = info_tag.find("p", class_="date")
        hour_tag = info_tag.find("p", class_="hour")
        place_tag = info_tag.find("p", class_="place")

        if not (date_tag and hour_tag and place_tag):
            continue

        date = date_tag.get_text(strip=True)
        hour = hour_tag.get_text(strip=True)
        place = place_tag.get_text(strip=True)

        try:
            datetime_obj = datetime.strptime(f"{date} {hour}", "%d-%m-%Y %H:%M")
        except ValueError:
            logging.warning(f"Failed to parse datetime from date='{date}' and hour='{hour}'")
            continue

        batch.append({"title": title, "datetime": datetime_obj.isoformat(), "place": place, "subtitles": subtitles})

    if batch:
        try:
            supabase.table("ep_meetings").insert(batch).execute()
            logging.info(f"Inserted {len(batch)} meeting(s) into ep_meetings")
        except Exception as e:
            logging.error(f"Error inserting meetings into Supabase: {e}")
    else:
        logging.info("No meetings found on this page")


scrape_meeting_calendar("21-05-2025", "26-05-2025")
