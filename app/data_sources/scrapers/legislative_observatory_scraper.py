import logging
import multiprocessing
from typing import Callable

import scrapy
from pydantic import BaseModel
from scrapy.crawler import CrawlerProcess

from app.data_sources.scraper_base import ScraperBase, ScraperResult


class LegislativeObservatory(BaseModel):
    id: str
    link: str | None = None
    title: str | None = None
    lastpubdate: str | None = None
    committee: str | None = None
    rapporteur: str | None = None
    embedding_input: str | None = None


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
            embedding_input = " ".join(
                filter(
                    None,
                    [
                        entry.xpath("./reference/text()").get(),
                        entry.xpath("./link/text()").get(),
                        entry.xpath("./title/text()").get(),
                        entry.xpath("./lastpubdate/text()").get(),
                        entry.xpath("./committee/committee/text()").get(),
                        entry.xpath("./rapporteur/rapporteur/text()").get(),
                    ],
                )
            )

            obj = LegislativeObservatory(
                id=entry.xpath("./reference/text()").get(),
                link=entry.xpath("./link/text()").get(),
                title=entry.xpath("./title/text()").get(),
                lastpubdate=entry.xpath("./lastpubdate/text()").get(),
                committee=entry.xpath("./committee/committee/text()").get(),
                rapporteur=entry.xpath("./rapporteur/rapporteur/text()").get(),
                embedding_input=embedding_input.strip() or None,
            )
            entries.append(obj)

        if self.result_callback:
            self.result_callback(entries)


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
