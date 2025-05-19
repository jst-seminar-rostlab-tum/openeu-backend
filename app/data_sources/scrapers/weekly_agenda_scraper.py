import datetime
import re
from collections.abc import Generator
from datetime import date, timedelta
from typing import Callable, Optional

import scrapy
from pydantic import BaseModel
from scrapy.crawler import CrawlerProcess
from scrapy.http import Response

# from app.core.supabase_client import supabase
# from supabase import Client  # type: ignore[attr-defined]


# ------------------------------
# Data Model
# ------------------------------


class AgendaEntry(BaseModel):
    type: str
    date: str
    time: Optional[str]
    title: str
    committee: Optional[str]
    location: Optional[str]
    topic: Optional[str]


# ------------------------------
# Scrapy Spider
# ------------------------------


class WeeklyAgendaSpider(scrapy.Spider):
    name = "weekly_agenda_spider"
    custom_settings = {"LOG_LEVEL": "INFO"}

    def __init__(
        self, start_date: date, end_date: date, result_callback: Optional[Callable[[list[AgendaEntry]], None]] = None
    ):
        super().__init__()
        self.start_date = start_date
        self.end_date = end_date
        self.result_callback = result_callback
        self.entries: list[AgendaEntry] = []

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        week_start = self.start_date
        while week_start <= self.end_date:
            iso_year, iso_week, _ = week_start.isocalendar()
            url = f"https://www.europarl.europa.eu/news/en/agenda/weekly-agenda/{iso_year}-{iso_week:02d}"
            yield scrapy.Request(url=url, callback=self.parse_week, meta={"week_start": week_start})
            week_start += timedelta(weeks=1)

    def closed(self, reason):
        if self.result_callback:
            self.result_callback(self.entries)

    def parse_week(self, response: Response):
        # Extract the week start date from the response meta
        current_week = response.meta["week_start"]
        print(f"Currently parsing week: {current_week}")

        # Iterate through each day in the week
        for day in response.css("li[id^=agenda-day]"):
            day_date_text = day.css("time::attr(datetime)").get()
            if not day_date_text:
                continue
            day_date = datetime.datetime.strptime(day_date_text, "%Y-%m-%d").date()
            print(f"Scraping day: {day_date}")

            for event in day.css("li.ep_gridrow"):
                # print for testing
                class_attr = event.attrib.get("class", "")

                # if there are no events of this type, skip
                if "ep-layout_noevent" in class_attr:
                    continue
                # if this is not an event, skip
                if "ep-layout_event" not in class_attr:
                    continue

                event_type = self.get_event_type(event)
                parser = self.get_parser_for_type(event_type)

                if parser:
                    entry = parser(event, day_date)
                    if entry:
                        self.entries.append(entry)
                        print("[SCRAPED]", entry.model_dump())
                        # Uncomment to store in supabase:
                        # supabase.table("WEEKLY_AGENDA").upsert(item.model_dump()).execute()

    def get_event_type(self, event: scrapy.Selector) -> str:
        class_attr = event.attrib.get("class", "")
        for cls in class_attr.split():
            if cls.startswith("ep-layout_event_"):
                return cls.replace("ep-layout_event_", "")
        return "unknown"

    def get_parser_for_type(self, event_type: str) -> Optional[Callable]:
        return {
            "plenary-session": self.parse_default_event,
            "president-diary": self.parse_president_diary,
            "conference-of-presidents": self.parse_default_event,
            "press-conferences": self.parse_default_event,
            "conciliation-committee": self.parse_default_event,
            "committee-meetings": self.parse_default_event,
            "delegations": self.parse_default_event,
            "public-hearings": self.parse_default_event,
            "other-events": self.parse_default_event,
            "official-visits": self.parse_default_event,
            "solemn-sittings": self.parse_default_event,
        }.get(event_type, self.parse_default_event)

    def parse_default_event(self, event: scrapy.Selector, date: date) -> Optional[AgendaEntry]:
        time = event.css("div.ep-layout_date time::text").get()
        committee = event.css("div.ep-layout_committee abbr::attr(title)").get()
        title = event.css("div.ep-layout_text span.ep_name::text").get()
        location = event.css("div.ep-layout_location span.ep_name::text").get()
        topics = event.css("div.ep-a_text li::text").getall()

        return AgendaEntry(
            date=date.isoformat(),
            time=time.strip() if time else None,
            title=title.strip(),
            committee=committee.strip() if committee else None,
            location=location.strip() if location else None,
            topic="; ".join(t.strip() for t in topics) if topics else None,
        )

    def parse_president_diary(self, event: scrapy.Selector, date: date) -> list[AgendaEntry]:
        entries = []

        for p in event.css("p.ep-wysiwig_paragraph::text"):
            full_text = p.get().strip()
            if not full_text:
                continue

            # Try to split time (e.g., "11:00 ...")
            time_match = re.match(r"^(\d{2}:\d{2})\s+(.*)", full_text)
            if time_match:
                time, text = time_match.groups()
            else:
                time, text = None, full_text

            entries.append(
                AgendaEntry(
                    type="President's agenda",
                    date=date.isoformat(),
                    time=time,
                    title=text,
                    committee=None,
                    location=None,
                    topic=None,
                )
            )

        return entries


# ------------------------------
# Scraping Function
# ------------------------------


def scrape_agenda(start_date: date, end_date: date) -> list[AgendaEntry]:
    if start_date > end_date:
        raise ValueError("start_date must be before or equal to end_date")

    results: list[AgendaEntry] = []

    def collect_results(entries):
        results.extend(entries)

    process = CrawlerProcess()
    process.crawl(WeeklyAgendaSpider, start_date=start_date, end_date=end_date, result_callback=collect_results)
    process.start()

    return results


# ------------------------------
# Main Function for Testing
# ------------------------------

if __name__ == "__main__":
    print("Scraping weekly agenda...")

    # Example: scrape from week 20 to 21
    start = datetime.date(2025, 3, 10)
    end = datetime.date(2025, 5, 26)

    entries = scrape_agenda(start_date=start, end_date=end)
    print(f"Total entries scraped: {len(entries)}")
