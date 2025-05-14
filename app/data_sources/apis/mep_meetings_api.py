import logging

import requests
from dateutil.parser import parse as parse_date

"""
### Important Note - Script is discontinued ###
This script fetches events from the European Parliament API and filters them based on a date range.
The API is not practical to work with, as it does not provide a way to filter events by date range directly.
Therefore, this script is discontinued and only checked into the repository for reference.
"""


api_url = "https://data.europarl.europa.eu/api/v2/events"


def get_date_at_offset(offset):
    logging.info(f"Fetching date at offset {offset}")
    params = {"format": "application/ld+json", "offset": offset, "limit": 1}
    response = requests.get(api_url, params=params)

    if response.status_code != 200:
        return None
    data = response.json().get("data", [])

    if not data:
        return None
    lite_event = data[0]
    start_date = fetch_event_date(lite_event["activity_id"])

    return start_date


def fetch_event_ids(offset, limit):
    logging.info(f"Fetching event IDs between offset {offset} and {offset + limit}")
    params = {"format": "application/ld+json", "offset": offset, "limit": limit}
    response = requests.get(api_url, params=params)
    if response.status_code != 200:
        return []
    return response.json().get("data", [])


def fetch_event_date(event_id):
    logging.info(f"Fetching date for event ID: {event_id}")
    params = {
        "format": "application/ld+json",
    }
    response = requests.get(api_url + "/" + event_id, params=params)
    if response.status_code != 200:
        return None
    date_str = response.json().get("data")[0].get("activity_date")
    return parse_date(date_str) if date_str else None


def binary_search(start_date, end_date, max_pages=125000):
    logging.info(f"Binary search for events between {start_date} and {end_date}")
    # Find the first page with date >= start_date
    low, high = 0, max_pages
    start_offset = None

    while low <= high:
        mid = (low + high) // 2
        date_at_mid = get_date_at_offset(mid)

        if date_at_mid is None:
            high = mid - 1
            continue
        if date_at_mid < start_date:
            low = mid + 1
        else:
            start_offset = mid
            high = mid - 1
    if start_offset is None:
        return None, None
    # Find the last page with date <= end_date
    low, high = start_offset, max_pages
    end_offset = None
    while low <= high:
        mid = (low + high) // 2
        date_at_mid = get_date_at_offset(mid)
        if date_at_mid is None:
            high = mid - 1
            continue
        if date_at_mid > end_date:
            high = mid - 1
        else:
            end_offset = mid
            low = mid + 1
    if end_offset is None:
        return None, None

    return start_offset, end_offset


def fetch_events_between(start_offset, end_offset):
    logging.info(f"Fetching events between offsets {start_offset} and {end_offset}")
    all_events = []
    limit = 100
    for offset in range(start_offset, end_offset + 1, limit):
        events = fetch_event_ids(offset, limit)
        all_events.extend(events)
    return all_events


if __name__ == "__main__":
    # Example usage
    start_date = parse_date("2023-01-01")
    end_date = parse_date("2023-01-31")

    # binary_search(start_date, end_date)
    start_offset, end_offset = 30562, 30612

    if start_offset is not None and end_offset is not None:
        events = fetch_events_between(start_offset, end_offset)
        print(f"Fetched {len(events)} events between {start_date} and {end_date}")
        for event in events:
            print(event)
    else:
        print("No events found in the given date range.")
