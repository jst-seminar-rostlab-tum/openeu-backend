from typing import Optional

from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from urllib.parse import quote
from supabase import create_client, Client
import requests
import os

BASE_URL_TEMPLATE = (
    "https://www.europarl.europa.eu/plenary/en/meetings-search.html?isSubmitted=true&dateFrom={date}"
    "&townCode=&loadingSubType=false&meetingTypeCode=&retention=TODAY&page={page}"
)

url: str = os.environ.get('LOCAL_SUPABASE_URL')
key: str = os.environ.get('LOCAL_ANON_KEY')
supabase: Client = create_client(url, key)


def scrape_meeting_calendar(start_date: str, end_date: str) -> None:
    start_date = datetime.strptime(start_date, '%d-%m-%Y')
    end_date = datetime.strptime(end_date, '%d-%m-%Y')

    current_date = start_date

    while current_date <= end_date:
        date_str = quote(current_date.strftime('%d/%m/%Y'))
        page_number = 0
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
    except requests.exceptions.RequestException:
        return None
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    error_message = soup.find('div', class_='message_error')
    if error_message and "No result" in error_message.get_text(strip=True):
        return None
    extract_meeting_info(soup)
    return soup


def extract_meeting_info(soup: BeautifulSoup) -> None:
    meetings_container = soup.find('div', class_='listcontent')
    meetings = meetings_container.find_all('div', class_='notice')

    batch = []

    for meeting in meetings:
        title_tag = meeting.find('p', class_='title')

        title = title_tag.getText(strip=True) if title_tag else None

        session_tag = meeting.find('div', class_='session')

        if not session_tag:
            continue

        subtitles_tag = session_tag.find('div', class_='subtitles')
        subtitles = subtitles_tag.get_text(strip=True) if subtitles_tag else None

        info_tag = session_tag.find('div', class_='info')

        if not info_tag:
            continue

        date_tag = info_tag.find('p', class_='date')
        hour_tag = info_tag.find('p', class_='hour')
        place_tag = info_tag.find('p', class_='place')

        if not (date_tag and hour_tag and place_tag):
            continue

        date = date_tag.get_text(strip=True)
        hour = hour_tag.get_text(strip=True)
        place = place_tag.get_text(strip=True)

        try:
            datetime_obj = datetime.strptime(f"{date} {hour}", "%d-%m-%Y %H:%M")
        except ValueError:
            continue

        batch.append({
            "title": title,
            "datetime": datetime_obj.isoformat(),
            "place": place,
            "subtitles": subtitles
        })

    if batch:
        supabase.table("ep_meetings").insert(batch).execute()