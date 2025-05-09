from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from supabase import create_client, Client
import requests
import os

url: str = os.environ.get('LOCAL_SUPABASE_URL')
key: str = os.environ.get('LOCAL_ANON_KEY')
supabase: Client = create_client(url, key)


def scrape_meeting_calendar(start_date: str, end_date: str):
    start_date = datetime.strptime(start_date, '%d-%m-%Y')
    end_date = datetime.strptime(end_date, '%d-%m-%Y')

    current_date = start_date

    while current_date <= end_date:
        date_str = current_date.strftime('%d%%2F%m%%2F%Y')

        base_url = (
            f"https://www.europarl.europa.eu/plenary/en/meetings-search.html?isSubmitted=true&dateFrom={date_str}"
            "&townCode=&loadingSubType=false&meetingTypeCode=&retention=TODAY&page=")

        page_number = 0
        while True:
            full_url = f"{base_url}{page_number}"
            page_soup = fetch_and_process_page(full_url)
            if page_soup is None:
                break
            page_number += 1

        current_date += timedelta(days=1)


def fetch_and_process_page(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    soup = BeautifulSoup(response.text, 'html.parser')
    error_message = soup.find('div', class_='message_error')
    if error_message and "No result" in error_message.get_text(strip=True):
        return None
    extract_meeting_info(soup)
    return soup


def extract_num_of_meetings(soup):
    results_span = soup.find('span', class_='results')
    if results_span:
        results_text = results_span.getText(strip=True)
        num_results = int(results_text.split(':')[1].strip())
        return num_results


def extract_meeting_info(soup):
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

        datetime_obj = datetime.strptime(f"{date} {hour}", "%d-%m-%Y %H:%M")

        data = {
            "title": title,
            "datetime": datetime_obj.isoformat(),
            "place": place,
            "subtitles": subtitles
        }

        supabase.table("meeting_calendar").insert(data).execute()