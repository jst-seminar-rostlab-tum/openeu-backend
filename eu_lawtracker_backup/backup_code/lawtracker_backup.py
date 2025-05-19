import scrapy, re, math, datetime as _dt
#from urllib.parse import quote, urljoin
from urllib.parse import urlencode, quote_plus
from eu_lawtracker.items import LawItem
#from scrapy_playwright.page import PageMethod

BASE = "https://law-tracker.europa.eu"

SEARCH = "https://law-tracker.europa.eu/api/procedures/search"
DETAIL = "https://law-tracker.europa.eu/api/procedures"


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

PAGE_SIZE = 50






""" class LawTrackerSpider(scrapy.Spider):
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
                started      = _dt.datetime.strptime(started,"%d/%m/%Y").date()
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
            ) """









class LawTrackerSpider(scrapy.Spider):
    name = "lawtracker"

    # completely bypass Playwright (and anything that might still be in project settings)
    custom_settings = {
        "CONCURRENT_REQUESTS": 8,
        "DOWNLOAD_DELAY": 0.25,
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "SmallBizLegisBot/0.3 (+contact@example.eu)",
            # -------- Ajax “finger-print” --------
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "*/*",
            "Referer": "https://law-tracker.europa.eu/",
            "Origin":  "https://law-tracker.europa.eu",
        },
        "DOWNLOAD_HANDLERS": {        # ← force Scrapy’s native HTTP handler
            "http":  "scrapy.core.downloader.handlers.http.HTTPDownloadHandler",
            "https": "scrapy.core.downloader.handlers.http.HTTPDownloadHandler",
        },
    }

    # ──────────────── helpers ────────────────
    def _search_req(self, code: str, page: int = 0):
        """Build one /procedures/search request (JSON)."""
        qs = urlencode(
            {
                "eurovoc": f'["{code},DOM"]',
                "page": page,
                "size": PAGE_SIZE,
                "lang": "en",
                "sort": "DOCD_DESC",
            },
            quote_via=quote_plus, safe="[]\","
        )
        url = f"{SEARCH}?{qs}"
        return scrapy.Request(
             url,
             headers={
                "Accept": "application/json",
                "X-Requested-With": "XMLHttpRequest",
         },
             cb_kwargs={"code": code, "page": page},
             callback=self.parse_search,
         )

    # ──────────────── first requests ────────────────
    def start_requests(self):
        for code in TOPICS:
            yield self._search_req(code, 0)

    # ──────────────── /procedures/search (JSON) ────────────────
    def parse_search(self, response: scrapy.http.Response, code: str, page: int):
        data = response.json()

        content_type = response.headers.get(b"Content-Type", b"").decode()
        if "json" not in content_type.lower():
        self.logger.error("NON-JSON response (%s) for %s", content_type, response.url)
        self.logger.error(response.text[:400])   # peek at body
        #return

        # individual procedure requests
        for proc in data["items"]:
            yield scrapy.Request(
                f"{DETAIL}/{proc['procedureId']}",
                cb_kwargs={"code": code, "overview": proc},
                callback=self.parse_detail,
            )

        # pagination
        last_page = math.ceil(data["totalHits"] / PAGE_SIZE) - 1
        if page < last_page:
            yield self._search_req(code, page + 1)

    # ──────────────── /procedures/{id} (JSON) ────────────────
    def parse_detail(self, response: scrapy.http.Response, code: str, overview: dict):
        detail = response.json()
        content_type = response.headers.get(b"Content-Type", b"").decode()
        if "json" not in content_type.lower():
        self.logger.error("NON-JSON response (%s) for %s", content_type, response.url)
        self.logger.error(response.text[:400])   # peek at body
        #return

        yield LawItem(
            procedure_id     = overview["procedureId"],
            title            = overview.get("title", ""),
            status           = overview.get("status", ""),
            started          = (_dt.date.fromisoformat(overview["started"])
                                if overview.get("started") else None),
            summary          = detail.get("summary"),
            last_stage_date  = (_dt.date.fromisoformat(detail["lastStageDate"])
                                if detail.get("lastStageDate") else None),
            committees       = detail.get("committees"),
            topic_codes      = [code],
        )












