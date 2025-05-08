from datetime import datetime

import requests
from bs4 import BeautifulSoup


def scrape_meeting_calendar(start_date: str, end_date: str):
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')

    url = "https://www.europarl.europa.eu/plenary/en/meetings-search.html?page=0&isSubmitted=true&dateFrom=21%2F05%2F2025&townCode=&loadingSubType=false&meetingTypeCode=&retention=TODAY"

    response = requests.get(url)

    if response.status_code != 200:
        print("Failed to retrieve the webpage.")
        return

    soup = BeautifulSoup(response.text, 'html.parser')

    meetings_container = soup.find('div', class_='listcontent')

    meetings = meetings_container.find_all('div', class_='notice')

    for meeting in meetings:
        title_tag = meeting.find('p', class_='title')
        title = title_tag.getText(strip=True) if title_tag else None

        session_tag = meeting.find('div', class_='session')

        subtitles_tag = session_tag.find('div', class_='subtitles')
        subtitles = subtitles_tag.get_text(strip=True) if subtitles_tag else None

        info_tag = session_tag.find('div', class_='info')
        date = info_tag.find('p', class_='date').get_text(strip=True) if info_tag else None
        hour = info_tag.find('p', class_='hour').get_text(strip=True) if info_tag else None
        place = info_tag.find('p', class_='place').get_text(strip=True) if info_tag else None

        print(f"Title: {title}")
        print(f"Date: {date}")
        print(f"Hour: {hour}")
        print(f"Place: {place}")
        print(f"Additional Info: {subtitles}")
        print("---------------")


scrape_meeting_calendar("2024-12-12","2025-01-01")