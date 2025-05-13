import logging

import scrapy
from postgrest.exceptions import APIError
from scrapy.crawler import CrawlerProcess

from app.core.supabase_client import supabase


class LegislativeObservatorySpider(scrapy.Spider):
    name = "legislative_observatory"
    start_urls = ["https://oeil.secure.europarl.europa.eu/oeil/en/search/export/XML?fullText.mode=EXACT_WORD&year=2025"]

    def parse(self, response):
        items = response.xpath("//item")
        for entry in items:
            data = {
                "REFERENCE": entry.xpath("./reference/text()").get(),
                "LINK": entry.xpath("./link/text()").get(),
                "TITLE": entry.xpath("./title/text()").get(),
                "LASTPUBDATE": entry.xpath("./lastpubdate/text()").get(),
                "COMMITTEE": entry.xpath("./committee/committee/text()").get(),
                "RAPPORTEUR": entry.xpath("./rapporteur/rapporteur/text()").get(),
            }

            self.upsert_record(data)

    def upsert_record(self, record):
        try:
            supabase.table("legislative_files").upsert(record).execute()
            logging.info(f"Upserted record: {record['reference']}")
        except APIError as e:
            logging.error(f"Supabase APIError: {e}")
        except Exception as e:
            logging.error(f"Unexpected error during upsert: {e}")


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(LegislativeObservatorySpider)
    process.start()
