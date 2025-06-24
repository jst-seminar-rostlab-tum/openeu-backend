import logging
import multiprocessing
from typing import Callable

import scrapy
from pydantic import BaseModel
from scrapy.crawler import CrawlerProcess

from app.data_sources.scraper_base import ScraperBase, ScraperResult
from app.core.supabase_client import supabase


class LegislativeObservatory(BaseModel):
    id: str
    link: str | None = None
    title: str | None = None
    lastpubdate: str | None = None
    committee: str | None = None
    rapporteur: str | None = None
    embedding_input: str | None = None


class LegislativeObservatoryDetail(BaseModel):
    id: str
    link: str | None = None
    title: str | None = None
    status: str | None = None
    subjects: list[str] | None = None
    key_players: list[dict] | None = None  # Assuming key_players is a list of dicts
    key_events: list[dict] | None = None


class LegislativeObservatorySpider(scrapy.Spider):
    name = "legislative_observatory"

    def __init__(self, result_callback: Callable[[LegislativeObservatory], None], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = [
            "https://oeil.secure.europarl.europa.eu/oeil/en/search/export/XML?fullText.mode=EXACT_WORD&year=2025"
        ]
        self.result_callback = result_callback

    def parse(self, response):
        entries = []
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

            entries.append(main_entry)

            yield scrapy.Request(
                url=f"https://oeil.secure.europarl.europa.eu/oeil/en/procedure-file?reference={id}",
                callback=self.parse_details_page,
                meta={"main_entry": main_entry},
            )

    def parse_details_page(self, response):
        main_entry: LegislativeObservatory = response.meta["main_entry"]
        id = main_entry.id

        status = response.css("p.text-danger::text").get()

        # Title is the one you already have from XML
        title = main_entry.title
        link = main_entry.link

        subject_block = response.xpath('//p[normalize-space(text())="Subject"]/following-sibling::p[1]').get()
        subjects_sel = scrapy.Selector(text=subject_block or "")
        subjects = [s.strip() for s in subjects_sel.xpath("//text()").getall() if s.strip()]

        # Key players table (just the Parliament section)
        key_players = []

        # Loop over each accordion item (i.e. institution section)
        for section in response.css("#erplAccordionKeyPlayers > ul > li.erpl_accordion-item"):
            institution = section.css("button span.t-x::text").get()
            if not institution:
                continue

            # Get the rows of the table under this institution
            rows = section.css("table tbody tr")
            for row in rows:
                committee_code = row.css("th .erpl_badge::text").get()
                committee_full = row.css("th a span::text").get()

                rapporteur = row.css("td:nth-child(2)::text").get()
                appointed = row.css("td:nth-child(3)::text").get()

                key_players.append(
                    {
                        "institution": institution.strip(),
                        "committee": committee_code.strip() if committee_code else None,
                        "committee_full": committee_full.strip() if committee_full else None,
                        "rapporteur": rapporteur.strip() if rapporteur else None,
                        "appointed": appointed.strip() if appointed else None,
                    }
                )

        # Key events
        key_events = []
        for row in response.css("#section3 table tbody tr"):
            cols = row.css("td")

            date = cols[0].css("::text").get(default="").strip()
            event = cols[1].css("::text").get(default="").strip()

            # Extract <a> inside the Reference column
            reference_link_tag = cols[2].css("a")
            reference_text = reference_link_tag.css("::text").get()
            reference_href = reference_link_tag.css("::attr(href)").get()

            summary = cols[3].css("::text").get(default="").strip() if len(cols) > 3 else None

            key_events.append(
                {
                    "date": date or None,
                    "event": event or None,
                    "reference": {
                        "text": reference_text.strip() if reference_text else None,
                        "link": reference_href.strip() if reference_href else None,
                    },
                    "summary": summary or None,
                }
            )

        detail_entry = LegislativeObservatoryDetail(
            id=id,
            link=link,
            title=title,
            status=status,
            subjects=subjects,
            key_players=key_players if key_players else None,
            key_events=key_events if key_events else None,
        )

        self.store_entry_to_table(detail_entry.model_dump(), table="legislative_files_details", on_conflict="id")

    def closed(self, reason):
        if self.result_callback:
            self.result_callback(self.entries)

    def store_entry_to_table(self, entry: dict, table: str, on_conflict="id"):
        try:
            supabase.table(table).upsert(entry, on_conflict=on_conflict).execute()
        except Exception as e:
            return str(e)
        return None


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
            scraper_error_result = self.store_entry(entry.model_dump(), on_conflict="id", embedd_entries=True)
            if scraper_error_result is None:
                self.entries.append(entry)
            else:
                self.logger.warning(f"Failed to store entry: {entry.id} -> {scraper_error_result}")


# ------------------------------
# Testing
# ------------------------------
if __name__ == "__main__":
    """
    neighbors = get_top_k_neighbors(
        query="Ukraine",
        allowed_sources={"legislative_files": "title"},
        k=3,
        sources=["document_embeddings"],  # triggers match_filtered
    )
    """
    print("Scraping Legislative Observatories...")
    scraper = LegislativeObservatoryScraper(stop_event=multiprocessing.Event())
    result = scraper.scrape_once(last_entry=None)

    if result.success:
        print(f"Scraping completed successfully. Total entries stored: {len(scraper.entries)}")
    else:
        print(f"Scraping failed with error: {result.error}")
