# eu_lawtracker/spiders/lawtracker.py
import scrapy
import re, json
from datetime import datetime
from urllib.parse import urlencode, quote, urljoin
from app.data_sources.scrapers.eu_lawtracker.items     import LawItem
from scrapy_playwright.page import PageMethod
from app.data_sources.scrapers.eu_lawtracker.pipelines import SupabasePipeline
import math
import datetime as dt

BASE = "https://law-tracker.europa.eu"
API    = f"{BASE}/api/procedures/search"
LANDING = f"{BASE}/"
SEARCH = f"{BASE}/api/procedures/search"
PAGE_SIZE = 50

TOPICS = {
    "04": "Politics",
    "08": "International relations",

    # "10": "European Union",
    # "12": "Law",
    # "16": "Economics",
    # "20": "Trade",
    # "24": "Finance",
    # "28": "Social Questions",
    # "32": "Education and Communications",
    # "36": "Science",
    # "40": "Business and Competition",
    # "44": "Employment and Working Conditions",
    # "48": "Transport",
    # "52": "Environment",
    # "56": "Agriculture, Forestry and Fisheries",
    # "60": "Agri-Foodstuffs",
    # "64": "Production, Technology and Research",
    # "66": "Energy",
    # "68": "Industry",
    # "72": "Geography",
    # "76": "International Organisations",
}



   
class LawTrackerSpider(scrapy.Spider):
    name = "lawtracker"
    custom_settings = {
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60_000,
        "CONCURRENT_REQUESTS": 4,          # safe because no clicks/JS events
    }

    def start_requests(self):
        params = (
            "searchType=topics&sort=DOCD_DESC&page=0&pageSize=50&lang=en"
        )
        for code in TOPICS:
            eurovoc = quote(f'["{code},DOM"]')     # → %5B%2204,DOM%22%5D
            url = f"{BASE}/results?eurovoc={eurovoc}&{params}"
            yield scrapy.Request(
                url,
                meta={
                    "playwright": True,
                    "playwright_page_methods": [
                        # only wait until Angular has rendered the cards
                        PageMethod("wait_for_selector", "app-procedure-card"),
                    ],
                    "topic_code": code,
                },
                callback=self.parse_search,
            )

    # ──────────────────────────────────────────────────────────────
    def parse_search(self, response):
        topic_code = response.meta["topic_code"]

        for card in response.css("div.result-card"):
            title_link = card.css("a::attr(href)").get()
            proc_id    = card.css("div.reference::text").get().strip()
            title      = " ".join(card.css("a::text").getall()).strip()
            status     = card.css("span.badge::text").get(default="").strip()
            started    = card.css("div:contains('Started')::text") \
                            .re_first(r"\d{2}/\d{2}/\d{4}")

            item = LawItem(
                procedure_id = proc_id,
                title        = title,
                status       = status,
                started_dt   = datetime.strptime(started, "%d/%m/%Y").date()
                                 if started else None,
                topic_codes  = [topic_code],
            )
            yield item

            # detail page (still needs Playwright because it’s Angular too)
            yield response.follow(
                urljoin(BASE, title_link),
                meta={"playwright": True, "item": item},
                callback=self.parse_detail
            )


        # pagination – increase `page=` until there are no more result cards
        m = re.search(r"[?&]page=(\d+)", response.url)
        if m and response.css("div.result-card"):
            next_page = int(m.group(1)) + 1
            next_url  = re.sub(r"[?&]page=\d+", f"&page={next_page}", response.url)
            yield response.follow(
                next_url,
                meta=response.meta,
                callback=self.parse_search,
            )
    
    def parse_detail(self, response):
            # you passed the LawItem in meta, so retrieve it…
            item = response.meta["item"]

            # (ADD!) extract more fields from the detail page here,
            # e.g. item["description"] = response.css("…").get()

            yield item


































