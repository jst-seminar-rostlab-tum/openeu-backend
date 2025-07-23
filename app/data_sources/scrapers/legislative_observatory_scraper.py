import logging
import multiprocessing
from typing import Callable

import scrapy
from pydantic import BaseModel
from scrapy.crawler import CrawlerProcess
from app.core.supabase_client import supabase

from app.data_sources.scraper_base import ScraperBase, ScraperResult
from app.models.legislative_file import KeyPlayer, KeyEvent, Rapporteur, Reference, DocumentationGateway
from app.core.mail.status_change import notify_status_change


# ------------------------------
# Data Model
# ------------------------------
class LegislativeObservatory(BaseModel):
    id: str
    link: str | None = None
    title: str | None = None
    lastpubdate: str | None = None
    details_link: str | None = None
    committee: str | None = None
    rapporteur: str | None = None
    status: str | None = None
    subjects: list[str] | None = None
    key_players: list[KeyPlayer] | None = None
    key_events: list[KeyEvent] | None = None
    documentation_gateway: list[DocumentationGateway] | None = None
    embedding_input: str | None = None


# ------------------------------
# Scrapy Spider
# ------------------------------
class LegislativeObservatorySpider(scrapy.Spider):
    name = "legislative_observatory"

    def __init__(self, result_callback: Callable[[LegislativeObservatory], None], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = ["https://oeil.secure.europarl.europa.eu/oeil/en/search/export/XML"]
        self.result_callback = result_callback
        self.entries: list[LegislativeObservatory] = []

    def parse(self, response):
        items = response.xpath("//item")

        for entry in items:
            id = entry.xpath("./reference/text()").get()
            link = entry.xpath("./link/text()").get()
            title = entry.xpath("./title/text()").get()
            lastpubdate = entry.xpath("./lastpubdate/text()").get()
            committee = entry.xpath("./committee/committee/text()").get()
            rapporteur = entry.xpath("./rapporteur/rapporteur/text()").get()
            embedding_input = " ".join(filter(None, [id, link, title, lastpubdate, committee, rapporteur]))

            main_entry = LegislativeObservatory(
                id=id,
                link=link,
                title=title,
                lastpubdate=lastpubdate,
                committee=committee,
                rapporteur=rapporteur,
                embedding_input=embedding_input,
            )

            yield scrapy.Request(
                url=f"https://oeil.secure.europarl.europa.eu/oeil/en/procedure-file?reference={id}",
                callback=self.parse_details_page,
                meta={"main_entry": main_entry},
            )

    def parse_details_page(self, response) -> None:
        main_entry: LegislativeObservatory = response.meta["main_entry"]

        # --- Status ---
        status = response.css("p.text-danger::text").get()
        main_entry.status = status.strip() if status else None

        # --- Link to details page ---
        main_entry.details_link = (
            f"https://oeil.secure.europarl.europa.eu/oeil/en/procedure-file?reference={main_entry.id}"
        )

        # --- Subjects ---
        subject_block = response.xpath('//p[normalize-space(text())="Subject"]/following-sibling::p[1]').get()
        subjects_sel = scrapy.Selector(text=subject_block or "")
        subjects = [s.strip() for s in subjects_sel.xpath("//text()").getall() if s.strip()]
        main_entry.subjects = subjects if subjects else None

        # --- Key Players ---
        key_players = []
        for section in response.css("#erplAccordionKeyPlayers > ul > li.erpl_accordion-item"):
            institution = section.css("button span.t-x::text").get()
            if not institution:
                continue

            rows = section.css("table tbody tr")
            for row in rows:
                # --- Committee Information ---
                committee_code = row.css("th .erpl_badge::text").get()
                committee_full = row.css("th a span::text").get()
                committee_link = row.css("th a::attr(href)").get()
                if committee_link and not committee_link.startswith("http"):
                    committee_link = response.urljoin(committee_link)

                # --- Rapporteurs ---
                rapporteurs = []
                main_links = row.css("td:nth-child(2) > a.rapporteur")
                for tag in main_links:
                    name = tag.css("span::text").get()
                    href = tag.attrib.get("href")
                    if name:
                        rapporteurs.append(Rapporteur(name=name.strip(), link=response.urljoin(href) if href else None))

                # --- Shadow Rapporteurs ---
                shadow_rapporteurs = []
                next_row = row.xpath("following-sibling::tr[1]")

                if next_row and "bg-none" in next_row.attrib.get("class", ""):
                    shadow_links = next_row.css("a.rapporteur")
                    for tag in shadow_links:
                        name = tag.css("span::text").get()
                        href = tag.attrib.get("href")
                        if name:
                            shadow_rapporteurs.append(
                                Rapporteur(name=name.strip(), link=response.urljoin(href) if href else None)
                            )

                # Couldn't extract appointed data, not important

                if committee_code:
                    key_players.append(
                        KeyPlayer(
                            institution=institution.strip(),
                            committee=committee_code.strip(),
                            committee_full=committee_full.strip() if committee_full else None,
                            committee_link=committee_link,
                            rapporteurs=rapporteurs or None,
                            shadow_rapporteurs=shadow_rapporteurs or None,
                        )
                    )

        main_entry.key_players = key_players if key_players else None

        # --- Key Events ---
        key_events = []
        for row in response.css("#section3 table tbody tr"):
            cols = row.css("td")

            date = cols[0].css("::text").get(default="").strip()
            event = cols[1].css("::text").get(default="").strip()

            reference_link_tag = cols[2].css("a")
            reference_text = reference_link_tag.css("::text").get()
            reference_href = reference_link_tag.css("::attr(href)").get()

            summary_link = row.css("td:nth-child(4) a::attr(href)").get()
            summary_link = response.urljoin(summary_link) if summary_link else None

            key_events.append(
                KeyEvent(
                    date=date or None,
                    event=event or None,
                    reference=Reference(
                        text=reference_text.strip() if reference_text else None,
                        link=reference_href.strip() if reference_href else None,
                    ),
                    summary=summary_link if summary_link else None,
                )
            )

        main_entry.key_events = key_events if key_events else None

        # --- Documentation gateway ---
        doc_gateway_entries = []
        for row in response.css("#erplAccordionDocGateway .table-responsive table tbody tr"):
            document_type = row.xpath("normalize-space(th[1])").get()
            reference_text = row.css("td:nth-child(2) a::text").get()
            reference_link = row.css("td:nth-child(2) a::attr(href)").get()
            date = row.css("td:nth-child(3)::text").get()
            summary_link = cols[3].css("a::attr(href)").get()
            summary_link = response.urljoin(summary_link) if summary_link else None

            doc_gateway_entries.append(
                DocumentationGateway(
                    document_type=document_type.strip() if document_type else None,
                    reference=Reference(
                        text=reference_text.strip() if reference_text else None,
                        link=response.urljoin(reference_link) if reference_link else None,
                    ),
                    date=date.strip() if date else None,
                    summary=summary_link if summary_link else None,
                )
            )

        main_entry.documentation_gateway = doc_gateway_entries if doc_gateway_entries else None

        # Extend embedding_input with details from the detail page
        embedding_additional = (
            [main_entry.status]
            + (main_entry.subjects or [])
            + [p.committee_full for p in main_entry.key_players or [] if p.committee_full]
            + [r.name for p in main_entry.key_players or [] for r in (p.rapporteurs or [])]
            + [r.name for p in main_entry.key_players or [] for r in (p.shadow_rapporteurs or [])]
            + [e.event for e in main_entry.key_events or [] if e.event]
            + [d.document_type for d in main_entry.documentation_gateway or [] if d.document_type]
            + [d.reference.text for d in main_entry.documentation_gateway or [] if d.reference and d.reference.text]
        )
        if main_entry.embedding_input is None:
            main_entry.embedding_input = ""

        main_entry.embedding_input += " " + " ".join(s for s in embedding_additional if s)

        # Check for status change
        old_record = supabase.table("legislative_files").select("status, title").eq("id", main_entry.id).execute()
        old_data = old_record.data[0] if old_record.data else None
        old_status = old_data["status"] if old_data else None

        if old_status and main_entry.status != old_status:
            notify_subscribers(main_entry=main_entry, old_status=old_status)

        # Return result
        self.entries.append(main_entry)

    def closed(self, reason):
        if self.result_callback:
            self.result_callback(self.entries)


def notify_subscribers(main_entry: LegislativeObservatory, old_status: str):
    subscription_check = supabase.table("subscriptions").select("user_id").eq("legislation_id", main_entry.id).execute()
    subscribers = subscription_check.data or []

    # Notify each user individually
    for sub in subscribers:
        user_id = sub["user_id"]
        notify_status_change(
            user_id=user_id,
            legislation={
                "id": main_entry.id,
                "title": main_entry.title,
                "link": main_entry.link,
                "details_link": main_entry.details_link,
                "status": main_entry.status,
            },
            old_status=old_status,
        )


# ------------------------------
# Scraper Base Implementation
# ------------------------------
class LegislativeObservatoryScraper(ScraperBase):
    def __init__(self, stop_event: multiprocessing.synchronize.Event):
        super().__init__(table_name="legislative_files", stop_event=stop_event)
        self.entries: list[LegislativeObservatory] = []
        self.logger = logging.getLogger(__name__)

    def scrape_once(self, last_entry=None, **kwargs) -> ScraperResult:
        try:
            process = CrawlerProcess(settings={"LOG_LEVEL": "INFO"})
            process.crawl(LegislativeObservatorySpider, result_callback=self._collect_entry)
            process.start()
            return ScraperResult(success=True, last_entry=self.entries[-1] if self.entries else None)
        except Exception as e:
            logging.exception("Failed to scrape legislative observatory")
            return ScraperResult(success=False, error=e)

    def _collect_entry(self, entries: list[LegislativeObservatory]):
        for entry in entries:
            scraper_error_result = self.store_entry(
                entry.model_dump(), on_conflict="id", embedd_entries=True, assign_topic=False
            )
            if scraper_error_result is None:
                self.entries.append(entry)
            else:
                self.logger.warning(f"Failed to store entry: {entry.id} -> {scraper_error_result}")


# ------------------------------
# Testing
# ------------------------------
if __name__ == "__main__":
    print("Scraping Legislative Observatories...")
    scraper = LegislativeObservatoryScraper(stop_event=multiprocessing.Event())
    result = scraper.scrape_once(last_entry=None)

    if result.success:
        print(f"Scraping completed successfully. Total entries stored: {len(scraper.entries)}")
    else:
        print(f"Scraping failed with error: {result.error}")
