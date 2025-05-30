# eu_lawtracker/spiders/lawtracker_topic_scraper.py
import re

# from typing import Generator
from datetime import datetime
from typing import Any
from urllib.parse import quote

import scrapy
from scrapy import Field, Item
from scrapy_playwright.page import PageMethod

from app.core.supabase_client import supabase
from app.data_sources.scraper_base import ScraperBase, ScraperResult

BASE = "https://law-tracker.europa.eu"
API = f"{BASE}/api/procedures/search"
LANDING = f"{BASE}/"
SEARCH = f"{BASE}/api/procedures/search"
PAGE_SIZE = 50

LAWS_TABLE = "eu_law_procedures"


TOPICS = {
    "04": "Politics",
    "08": "International relations",
    "10": "European Union",
    "12": "Law",
    "16": "Economics",
    "20": "Trade",
    "24": "Finance",
    "28": "Social Questions",
    "32": "Education and Communications",
    "36": "Science",
    "40": "Business and Competition",
    "44": "Employment and Working Conditions",
    "48": "Transport",
    "52": "Environment",
    "56": "Agriculture, Forestry and Fisheries",
    "60": "Agri-Foodstuffs",
    "64": "Production, Technology and Research",
    "66": "Energy",
    "68": "Industry",
    "72": "Geography",
    "76": "International Organisations",
}


class LawItem(Item):
    procedure_id = Field()
    title = Field()
    status = Field()
    active_status = Field()
    started_date = Field()
    topic_codes = Field()
    topic_labels = Field()
    embedding_input = Field()


class LawTrackerSpider(scrapy.Spider, ScraperBase):
    name = "topic_lawtracker"
    custom_settings = {
        # Playwright settings
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60_000,
        "CONCURRENT_REQUESTS": 4,
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, *args, **kwargs):
        scrapy.Spider.__init__(self, *args, **kwargs)
        ScraperBase.__init__(self, table_name=LAWS_TABLE)
        # self._db = ScraperBase(table_name=LAWS_TABLE)

    def scrape_once(self, last_entry: Any, **args: Any) -> ScraperResult:
        """
        Scrape the law tracker by topic codes.
        This method is called by the ScraperBase to perform the scraping.
        """
        self.logger.info("Starting LawTrackerSpider scrape...")

        for req in self.start_requests():
            # 'self.crawler' is available once the spider is running
            self.crawler.engine.crawl(req, spider=self)

        self.logger.info("LawTrackerSpider scrape completed.")
        return ScraperResult(success=True, last_entry=last_entry)

    def start_requests(self):
        params = "searchType=topics&sort=DOCD_DESC&page=0&pageSize=50&lang=en"
        for code in TOPICS:
            eurovoc = quote(f'["{code},DOM"]')  # → %5B%2204,DOM%22%5D
            url = f"{BASE}/results?eurovoc={eurovoc}&{params}"
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        # wait for the result cards to load (unsure of which elemt to wait for for optimal performance,
                        # I tried a few but waiting for: "div.result-card div.title-color"
                        # proved to be reliable and the fastest by my testing)
                        PageMethod("wait_for_selector", "div.result-card div.title-color"),
                        # PageMethod("wait_for_selector", "div.result-card", state="attached")
                    ],
                    "topic_code": code,
                },
                callback=self.parse_search,
            )

    # ──────────────────────────────────────────────────────────────
    def parse_search(self, response):
        topic_code = response.meta["topic_code"]
        topic_label = TOPICS[topic_code]

        for card in response.css("div.result-card"):
            proc_id = card.css("div.reference::text").get().strip()
            title = card.xpath("normalize-space(.//div[contains(@class,'title-color')])").get("")
            status = card.xpath("normalize-space(.//div[contains(@class,'status')]/span)").get("")
            active_status = card.css("span.active-status::text").get(default="").strip()
            started_text = card.css("div:contains('Started')::text").re_first(r"\d{2}/\d{2}/\d{4}")
            started_date = datetime.strptime(started_text, "%d/%m/%Y").date() if started_text else None

            item = LawItem(
                procedure_id=proc_id,
                title=title,
                status=status,
                active_status=active_status,
                started_date=started_date,
                topic_codes=[topic_code],
                topic_labels=[topic_label],
                embedding_input=(
                    f'{proc_id} "{title}", '
                    f'status: {status or "n/a"}, '
                    f'active: {active_status or "n/a"}, '
                    f'started: {started_date or "n/a"}, '
                    f'topics: {topic_label}'
                ),
            )
            self.upsert_law(dict(item))  # write/update function
            yield item

        # pagination – increase `page=` until there are no more result cards
        m = re.search(r"[?&]page=(\d+)", response.url)
        if m and response.css("div.result-card"):
            next_page = int(m.group(1)) + 1
            next_url = re.sub(r"[?&]page=\d+", f"&page={next_page}", response.url)
            yield response.follow(
                next_url,
                meta=response.meta,
                callback=self.parse_search,
            )

    def parse_detail(self, response):
        item = response.meta["item"]
        yield item

    def normalise(self, item: dict) -> dict:
        item = item.copy()
        item["title"] = " ".join(item["title"].split())
        item["status"] = item["status"].lower()
        item["active_status"] = item["active_status"].lower() if item.get("active_status") else None
        # return item
        # JSON‐serialize the date
        if item.get("started_date"):
            item["started_date"] = item["started_date"].isoformat()
        return item

    def upsert_law(self, item: dict) -> None:
        """
        Insert a new procedure or overwrite the existing row
        whenever any field (except id) has changed.
        Diff. procedure_id = new row (new procedure)
        """
        data = self.normalise(item)
        if isinstance(data.get("started_date"), datetime):
            data["started_date"] = data["started_date"].isoformat()
        pid = data["procedure_id"]

        # ── 1. fetch if exists ─────────────────────────────
        res = (
            supabase.table(LAWS_TABLE)
            .select("id, title, status, active_status, started_date, topic_codes, topic_labels, embedding_input")
            .eq("procedure_id", pid)
            .limit(1)
            .execute()
        )

        if not res.data:
            # new -> INSERT
            supabase.table(LAWS_TABLE).insert(data).execute()
            return

        row = res.data[0]

        # ── 2. merge topic codes ─────────────────────────
        merged_codes = sorted({*(row["topic_codes"] or []), *data["topic_codes"]})
        merged_labels = sorted({*(row["topic_labels"] or []), *data["topic_labels"]})

        data["topic_codes"] = merged_codes
        data["topic_labels"] = merged_labels

        # ── 3. compare every relevant field (other than id) ──────────────────────────
        has_changed = any(
            [
                row["title"] != data["title"],
                row["status"] != data["status"],
                row["active_status"] != data["active_status"],
                str(row["started_date"]) != str(data["started_date"]),
                row["topic_codes"] != data["topic_codes"] or row["topic_labels"] != data["topic_labels"],
                row["embedding_input"] != data["embedding_input"],
            ]
        )

        if not has_changed:
            return

        # ── 4. overwrite the row with merged topics ─────────────────────────────────────
        # self._db.store_entry(item, on_conflict="procedure_id")
        err = self.store_entry(data, on_conflict="procedure_id")
        if err:
            self.logger.error(f"Upsert failed for {item['procedure_id']}: {err.error}")

        # manual update code if needed, now using store_entry() instead
        # supabase.table(LAWS_TABLE).update({**data, "updated_at": dt.datetime.now(dt.timezone.utc)}).eq(
        #     "id", row["id"]
        # ).execute()
