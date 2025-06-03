import re
from collections.abc import Generator
from datetime import date, datetime, timedelta
from typing import Any, Optional

import scrapy
from pydantic import BaseModel
from w3lib.html import remove_tags

from app.core.supabase_client import supabase
from app.data_sources.scraper_base import ScraperBase, ScraperResult

# from app.core.deepl_translator import translate_text
from scripts.embedding_generator import embed_row


class MeetingModel(BaseModel):
    id: str
    meeting_type: Optional[str] = None
    title: str
    start_datetime: datetime
    end_datetime: Optional[datetime] = None
    location: Optional[str] = None
    link: str
    attachments_url: Optional[list[str]] = []
    commission: Optional[str] = None
    agenda: Optional[list[str]] = []
    ministers: Optional[list[str]] = []
    attendees: Optional[list[str]] = []
    original_content: str
    translated_content: str
    embedding_input: Optional[str] = None
    start_time: str
    end_time: str


class NetherlandsTwkaMeetingsScraper(scrapy.Spider, ScraperBase):
    """
    “Plain” Scrapy spider (no Playwright) to scrape https://www.tweedekamer.nl/debat_en_vergadering by date.
    Uses the exact HTML structure provided (div.m-tv-guide__item.js-clickable, data-start/data-end attributes, etc.).
    """

    name = "netherlands_tweedekamer_meetings_scaper"

    # Base URL for agenda (+ later append “?date=YYYY-MM-DD”)
    BASE_AGENDA_URL = "https://www.tweedekamer.nl/debat_en_vergadering"

    def __init__(self, start_date: date, end_date: date, *args, **kwargs):
        scrapy.Spider.__init__(self, *args, **kwargs)
        ScraperBase.__init__(self, table_name="nl_twka_meetings")

        # store the date‐range to scrape
        self.start_date = start_date
        self.end_date = end_date

    def start_requests(self) -> Generator[scrapy.Request, None, None]:
        """
        When run via `scrapy runspider`, Scrapy looks here for initial requests.
        """
        yield from self.scrape_once(last_entry=None)

    def scrape_once(  # type: ignore[override]
        self,
        last_entry: Any,
        **args: Any,
    ) -> Generator[scrapy.Request, None, ScraperResult]:
        """
        Called by ScraperBase.  Instead of using `last_entry`,
        loops exactly from self.start_date through self.end_date (inclusive),
        emitting one Request per date.
        """
        # 1) Convert the two string‐inputs into date objects
        start_date = (
            datetime.fromisoformat(self.start_date).date() if isinstance(self.start_date, str) else self.start_date
        )
        end_date = datetime.fromisoformat(self.end_date).date() if isinstance(self.end_date, str) else self.end_date

        # 2) range is empty -> terminate
        if start_date > end_date:
            self.logger.info("No dates to scrape (start_date > end_date).")
            return ScraperResult(success=True, last_entry=None)

        # 3) Otherwise, generate a request for each day within argument dates
        current = start_date
        while current <= end_date:
            formatted = current.strftime("%d-%m-%Y")  # e.g. "02-06-2025"
            url = f"{self.BASE_AGENDA_URL}?date={formatted}"
            yield scrapy.Request(
                url=url,
                callback=self.parse_agenda,
                cb_kwargs={"agenda_date": current},
            )
            current += timedelta(days=1)
        return ScraperResult(success=True, last_entry=None)

    def parse_agenda(self, response: scrapy.http.Response, agenda_date: date):
        """
        Parse the agenda page for a single date.  Looks for all
        <div class="m-tv-guide__item js-clickable"> blocks and extracts:
          - detail‐page URL
          - meeting_type (e.g. "Notaoverleg")
          - commission name
          - data-start / data-end (start/end times)
        Then schedules a Request to parse_meeting() for each block.
        """
        self.logger.info(f"[NoJS] Parsing agenda for {agenda_date.isoformat()}")

        # 1) Select every “meeting block” on this date
        blocks = response.css("div.m-tv-guide__item.js-clickable")
        if not blocks:
            self.logger.info(f"No meetings found on {agenda_date.isoformat()}.")
            return

        for block in blocks:
            # 2) Extract the detail‐page link from inside <h3 class="m-tv-guide__title"><a href="">
            rel_link = block.css("h3.m-tv-guide__title a::attr(href)").get()
            if not rel_link:
                self.logger.warning("No <a href> found inside m-tv-guide__title; skipping this block.")
                continue

            detail_url = response.urljoin(rel_link)
            meeting_id = detail_url.rstrip("/").split("=")[-1]  # e.g. "2024A05042"

            # 3) Extract “type” (Notaoverleg, etc.)
            meeting_type = block.css("span.m-tv-guide__type::text").get()
            if meeting_type:
                meeting_type = meeting_type.strip()

            # 4) Extract “commission”
            commission = block.css("div.m-tv-guide__commission::text").get()
            if commission:
                commission = commission.strip()

            # 5) Extract start/end times from the block
            start_time = block.attrib.get("data-start", "").strip()
            end_time = block.attrib.get("data-end", "").strip()

            # 6) Schedule a Request for the detail page, passing along these fields in cb_kwargs
            yield scrapy.Request(
                url=detail_url,
                callback=self.parse_meeting,
                cb_kwargs={
                    "meeting_id": meeting_id,
                    "agenda_date": agenda_date,
                    "meeting_type": meeting_type,
                    "commission": commission,
                    "start_time": start_time,
                    "end_time": end_time,
                },
            )

    def parse_meeting(
        self,
        response: scrapy.http.Response,
        meeting_id: str,
        agenda_date: date,
        meeting_type: Optional[str],
        commission: Optional[str],
        start_time: Optional[str],
        end_time: Optional[str],
    ) -> None:
        """
        Parse the detail page for a single meeting.  It looks to be fully server‐rendered,
        so everything is in the HTML.
        """

        self.logger.info(f"[NoJS] Parsing detail for ID={meeting_id}")

        # ── 1) Title
        # Find the <span class="h-visually-hidden">, take the next node:
        title: str = (
            response.xpath(
                "normalize-space(//h1/span[contains(@class,'h-visually-hidden')]/following-sibling::text()[1])"
            )
            .get(default="")
            .strip()
        )

        if not title:
            title = response.xpath("normalize-space(//h1)").get(default="").strip()

        # ── 2) Build both start_datetime and end_datetime
        try:
            if start_time:
                hh_s, mm_s = start_time.split(":")
                start_dt: datetime = datetime(
                    agenda_date.year,
                    agenda_date.month,
                    agenda_date.day,
                    int(hh_s),
                    int(mm_s),
                )
            else:
                # if start_time is missing, default to midnight of agenda_date
                start_dt = datetime.combine(agenda_date, datetime.min.time())
        except Exception:
            self.logger.warning(f"Could not parse start_time={start_time!r}; using agenda_date at midnight.")
            start_dt = datetime.combine(agenda_date, datetime.min.time())

        end_dt: Optional[datetime]
        try:
            # parse end_time
            if end_time:
                hh_e, mm_e = end_time.split(":")
                end_dt = datetime(
                    agenda_date.year,
                    agenda_date.month,
                    agenda_date.day,
                    int(hh_e),
                    int(mm_e),
                )
            else:
                # if no end_time is provided
                end_dt = None
        except Exception:
            self.logger.warning(f"Could not parse end_time={end_time!r}; leaving end_datetime as None.")
            end_dt = None

        # ── 3) Location (updated selector)
        # detail page wraps “Locatie:” in <strong>, e.g.
        #   <strong>Locatie:</strong> Thorbeckezaal
        location: Optional[str] = (
            response.xpath(
                "normalize-space(//strong[contains(normalize-space(.), 'Locatie:')]/following-sibling::text()[1])"
            )
            .get(default="")
            .strip()
        )

        if not location:
            # If for some reason the <strong> approach fails, fallback to looking
            # for “Locatie:” anywhere in the page and scraping what comes after it:
            location = (
                response.xpath("normalize-space(//*[contains(text(), 'Locatie')]/text()[normalize-space(.)][2])")
                .get(default="")
                .strip()
            )

        # If still empty, you know there is no “Locatie:”
        if location == "":
            location = None

        # ── 4) Override 'commission' by extracting from the detail page HTML.
        # look for: <strong>Commissie:</strong> <a href="…">…</a>
        detail_comm = response.xpath(
            "normalize-space(//strong[ normalize-space(text())='Commissie:']/following-sibling::a[1]/text())"
        ).get()
        if detail_comm:
            commission = detail_comm.strip()
        else:
            # Fallback to plain text if there is no <a> immediately after <strong>
            fallback_comm = response.xpath(
                "normalize-space(//strong[normalize-space(text())='Commissie:']/following-sibling::text()[1])"
            ).get()
            if fallback_comm:
                commission = fallback_comm.strip()

        # ── 5.2) Attachments
        # get download‐URL for all PDFs under the “m-list” container.
        attachments_url = [
            response.urljoin(href.strip())
            for href in response.css("ul.m-list--has-dividers li.m-list__item--variant-download a::attr(href)").getall()
            if href and href.strip()
        ]

        # ── 5.3) Agenda (“speaking‐time”) lines
        # Look up the <div class="u-mt-4 h-flow"> block (if exists, some meetings do not have it).
        agenda_items: list[str] = []
        flow_div = response.xpath(
            "//div[contains(concat(' ', normalize-space(@class), ' '), ' u-mt-4 ')"
            " and contains(concat(' ', normalize-space(@class), ' '), ' h-flow ')]"
        )
        if flow_div:
            # 1) Grab full HTML (might contain <br> separators)
            flow_div_html = flow_div.get() or ""

            # 2) Split on every <br> or <br/> tag
            parts = re.split(r"<br\s*/?>", flow_div_html, flags=re.IGNORECASE)
            for segment in parts:
                # 3) Remove any HTML tags, then strip
                raw = remove_tags(segment).strip()
                # 3a) Collapse any run of whitespace into one space
                text = re.sub(r"\s+", " ", raw)
                if not text:
                    continue
                # 4) Drop any spurious “Loading data” that showed up during testing
                if "loading data" in text.lower():
                    continue
                # 5) whats left is a valid agenda line
                agenda_items.append(text)

        # ── 5.4) Ministers (“Bewindsperso(o)n(en)”)
        ministers: list[str] = []
        # locate <h2> where text contains "Bewindsperso"
        header = response.xpath("//h2[normalize-space(text())='Bewindsperso(o)n(en)']")
        if header:
            # find all <span class="m-list__label"> elements under <ul> + after that <h2>
            span_labels = header.xpath("following-sibling::ul[1]//span[contains(@class,'m-list__label')]")
            for span in span_labels:
                # Each <span> has two text‐nodes separated by a <br>:
                lines = span.xpath("text()").getall()
                parts = [ln.strip() for ln in lines if ln.strip()]
                if not parts:
                    continue
                # 5) If there are at least 2 parts, treat them as [Name, Title]
                if len(parts) >= 2:
                    name = parts[0]
                    title = parts[1]
                    ministers.append(f"{name} ({title})")
                else:
                    # Fallback: if only one non‐empty line was found
                    ministers.append(parts[0])
        # If no header was found, ministers stays an empty list

        # ── 5.5) Attendees (“Deelnemers”)
        attendees: list[str] = []
        attendee_header = response.xpath("//h2[normalize-space(text())='Deelnemers']")
        if attendee_header:
            span_labels = attendee_header.xpath("following-sibling::ul[1]//span[contains(@class,'m-list__label')]")
            for span in span_labels:
                lines = span.xpath("text()").getall()
                parts = [ln.strip() for ln in lines if ln.strip()]
                if parts:
                    attendees.append(", ".join(parts))

        # ── 6) Original content (Dutch transcript)
        original_paras = response.css("div.meeting-content p::text").getall()
        original_content_text = "\n\n".join([p.strip() for p in original_paras if p.strip()])

        # ── 7) Translate via DeepL
        translated_content_text = ""
        if original_content_text:
            try:
                # translated_content_text = translate_text(original_content_text, target_lang="EN")
                pass
            except Exception as e:
                self.logger.error(f"DeepL translation failed for ID={meeting_id}: {e}")
                translated_content_text = ""

        # Prepare a dict mapping for the embedding_input → value (use "n/a" if str is empty)
        embedding_map: dict[str, str] = {
            "id": meeting_id,
            "type": meeting_type or "n/a",
            "title": title,
            "commission": commission or "n/a",
            "agenda": "; ".join(agenda_items) if agenda_items else "n/a",
            "ministers": "; ".join(ministers) if ministers else "n/a",
            "attendees": "; ".join(attendees) if attendees else "n/a",
            "content": original_content_text or "n/a",
        }
        embedding_input = ", ".join(f"{label}: {val}" for label, val in embedding_map.items())

        # ── 8) Build the Pydantic model
        data_dict: dict[str, Any] = {
            "id": meeting_id,
            "meeting_type": meeting_type,
            "title": title,
            "start_datetime": start_dt,
            "end_datetime": end_dt,
            "location": location,
            "link": response.url,
            "attachments_url": attachments_url,
            "commission": commission,
            "agenda": agenda_items,
            "ministers": ministers,
            "attendees": attendees,
            "original_content": original_content_text,
            "translated_content": translated_content_text,
            "embedding_input": embedding_input,
            "start_time": start_time,
            "end_time": end_time,
        }

        try:
            meeting_item = MeetingModel(**data_dict)
        except Exception as e:
            self.logger.error(f"Pydantic validation error for meeting {meeting_id}: {e}")
            return

        # ── 9) Upsert into Supabase (no duplicates, compare fields, embed if changed)
        self.upsert_meeting(meeting_item)

    def upsert_meeting(self, item: MeetingModel) -> None:
        """
        Insert or update the "nl_twka_meetings" row in Supabase for this meeting.
        Compare every field except “id” to decide update.
        After insert/update, call embed_row(data) to generate embeddings.
        """

        # 1) Prepare a plain dict for Supabase
        data = {
            "id": item.id,
            "meeting_type": item.meeting_type,
            "title": item.title,
            "start_datetime": item.start_datetime.isoformat(),
            "end_datetime": (item.end_datetime.isoformat() if item.end_datetime else None),
            "location": item.location,
            "link": item.link,
            "attachments_url": item.attachments_url,
            "commission": item.commission,
            "agenda": item.agenda,
            "ministers": item.ministers,
            "attendees": item.attendees,
            "original_content": item.original_content,
            "translated_content": item.translated_content,
            "embedding_input": item.embedding_input,
            "start_time": item.start_time,
            "end_time": item.end_time,
        }

        # 2) Check if this ID already exists
        resp = (
            supabase.table(self.table_name)
            .select(
                "title, meeting_type, start_datetime, end_datetime, location, link, "
                "attachments_url, commission, agenda, ministers, attendees, "
                "original_content, translated_content, embedding_input, start_time, end_time"
            )
            .eq("id", item.id)
            .limit(1)
            .execute()
        )

        if not resp.data:
            # row does not exist -> INSERT
            self.logger.info(f"[INSERT] New meeting id={item.id} at {item.start_datetime.isoformat()}")
            supabase.table(self.table_name).insert(data).execute()

            # Generate embedding for the new row
            try:
                embed_row(self.table_name, item.id, "embedding_input", item.embedding_input or "")
            except Exception as e:
                self.logger.error(f"Embedding generation failed for id={item.id}: {e}")
            return

        # 3b) Row exists → compare every relevant field in one shot
        existing: dict[str, Any] = resp.data[0]

        # Helper to guard .strip() on an Optional[str]
        def _as_str(x: Any) -> str:
            return x.strip() if isinstance(x, str) else ""

        # single boolean that is True if any field changed
        has_changed = any(
            [
                (existing.get("meeting_type") or "") != (data["meeting_type"] or ""),
                (existing.get("title") or "") != (data["title"] or ""),
                _as_str(existing.get("start_datetime")) != data["start_datetime"],
                _as_str(existing.get("end_datetime")) != (data["end_datetime"] or ""),
                _as_str(existing.get("location")) != (data["location"] or ""),
                _as_str(existing.get("link")) != (data["link"] or ""),
                _as_str(existing.get("commission")) != (data["commission"] or ""),
                _as_str(existing.get("start_time")) != (data["start_time"] or ""),
                _as_str(existing.get("end_time")) != (data["end_time"] or ""),
                _as_str(existing.get("embedding_input")) != _as_str(data["embedding_input"]),
                # list fields (compare sorted lists)
                (sorted(existing.get("attachments_url") or []) != sorted(data["attachments_url"] or [])),
                (sorted(existing.get("agenda") or []) != sorted(data["agenda"] or [])),
                (sorted(existing.get("ministers") or []) != sorted(data["ministers"] or [])),
                (sorted(existing.get("attendees") or []) != sorted(data["attendees"] or [])),
                _as_str(existing.get("original_content")) != _as_str(item.original_content),
                _as_str(existing.get("translated_content")) != _as_str(item.translated_content),
            ]
        )

        if not has_changed:
            self.logger.info(f"[SKIP] id={item.id} already up‐to‐date.")
            return

        # 3c) Something changed → UPSERT (on_conflict="id")
        self.logger.info(f"[UPDATE] id={item.id} – fields changed -> updating row.")
        err = self.store_entry(data, on_conflict="id")
        if err:
            self.logger.error(f"Supabase UPSERT failed for id={item.id}: {err.error}")
            return

        # Regenerate embedding for the updated row
        try:
            embed_row(self.table_name, item.id, "embedding_input", item.embedding_input or "")
        except Exception as e:
            self.logger.error(f"Embedding update failed for id={item.id}: {e}")
