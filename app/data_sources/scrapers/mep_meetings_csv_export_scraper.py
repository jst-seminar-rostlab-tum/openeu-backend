import csv
import logging
import os
from datetime import date, datetime
from typing import TypedDict

import requests

"""
### Important Note - Script is discontinued ###
This script fetches from the MEP meetings search CSV export and filters them based on a date range.
The CSV export is not practical to work with, as it does not include the meeting location - despite location being 
shown in the search results UI. Therefore, this script is discontinued in favor of a scrapy scraper and only checked 
into the repository for reference.
"""


class MEPMeeting(TypedDict):
    """
    TypedDict for MEP Meeting data.
    """

    title: str
    member_id: str
    member_name: str
    meeting_date: date
    member_capacity: str
    procedure_reference: str | None
    attendees: list[str]
    # renamed from lobbyist_id to lobbyist_ids to clarify that it is a list
    lobbyist_ids: list[str]


def __parse_meeting(raw: dict[str, str]) -> MEPMeeting:
    return MEPMeeting(
        title=raw["title"],
        member_id=raw["member_id"],
        member_name=raw["member_name"],
        meeting_date=datetime.strptime(raw["meeting_date"], "%Y-%m-%d").date(),
        member_capacity=raw["member_capacity"],
        procedure_reference=raw["procedure_reference"] if raw["procedure_reference"] != "" else None,
        attendees=[] if raw["attendees"] == "" else [a.strip() for a in raw["attendees"].split("|")],
        lobbyist_ids=[] if raw["lobbyist_id"] == "" else [a.strip() for a in raw["lobbyist_id"].split("|")],
    )


def __is_valid_date_range(start_date: date, end_date: date) -> bool:
    if not start_date or not end_date:
        logging.error("Invalid date range")
        return False
    if start_date > end_date:
        logging.error("Start date is after end date")
        return False
    return True


def __build_meeting_url(start_date: date, end_date: date) -> str:
    date_format = "%d/%m/%Y"
    url_template = (
        "https://www.europarl.europa.eu/meps/en/search-meetings?textualSearch=&fromDate={}&toDate={}&exportFormat=CSV"
    )
    return url_template.format(start_date.strftime(date_format), end_date.strftime(date_format))


def __download_csv(url: str, filename: str) -> bool:
    response = requests.get(url)
    if response.status_code != 200:
        logging.error(f"Failed to fetch meetings: {response.status_code}")
        return False
    with open(filename, "wb") as f:
        f.write(response.content)
    logging.info(f"CSV file saved as {filename}")
    return True


def __parse_csv_to_meetings(filename: str) -> list:
    meetings = []
    with open(filename) as f:
        reader = csv.reader(f)
        headers = next(reader)
        for row in reader:
            raw_meeting = {headers[i]: row[i] for i in range(len(headers))}
            meeting = __parse_meeting(raw_meeting)
            meetings.append(meeting)
    logging.info(f"Parsed {len(meetings)} meetings")
    return meetings


def __get_meetings_in_timespan(start_date: date, end_date: date) -> list[MEPMeeting]:
    if not __is_valid_date_range(start_date, end_date):
        return []

    logging.info(f"Fetching meetings between {start_date} and {end_date}")
    url = __build_meeting_url(start_date, end_date)
    logging.info(f"Fetching meetings from URL: {url}")

    filename = "meetings.csv"
    if not __download_csv(url, filename):
        return []

    meetings = __parse_csv_to_meetings(filename)

    # clean up
    os.remove(filename)
    logging.info(f"CSV file {filename} removed")

    return meetings


if __name__ == "__main__":
    # Example usage
    start_date = date(2023, 10, 31)
    end_date = date(2023, 10, 31)
    meetings = __get_meetings_in_timespan(start_date, end_date)
    for meeting in meetings:
        print(f"Title: {meeting['title']}")
        print(f"Member ID: {meeting['member_id']}")
        print(f"Member Name: {meeting['member_name']}")
        print(f"Meeting Date: {meeting['meeting_date']}")
        print(f"Member Capacity: {meeting['member_capacity']}")
        print(f"Procedure Reference: {meeting['procedure_reference']}")
        print(f"Attendees: {meeting['attendees']}")
        print(f"Lobbyist IDs: {meeting['lobbyist_ids']}")
        print("------------")
