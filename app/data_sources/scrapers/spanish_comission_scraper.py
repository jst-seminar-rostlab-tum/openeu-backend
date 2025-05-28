# ------------------------------
# Data Model
# ------------------------------
"""
class CommissionAgendaEntry(BaseModel):
"""
# ------------------------------
# Scrapy Spider
# ------------------------------

"""
class SpanishCommissionSpider(scrapy.Spider):
    name = "spanish_commission_spider"
    custom_settings = {"LOG_LEVEL": "INFO"}

    def __init__(self, target_date: date, result_callback: Optional[Callable] = None):
        super().__init__()

    def start_requests(self) -> Generator[scrapy.Request, None, None]:


    def closed(self, reason):


    def parse_date(self, response: Response):
"""

# ------------------------------
# Scraper Base Implementation
# ------------------------------

"""
class SpanishCommissionScraper(ScraperBase):
    def __init__(self, target_date: date):
        super().__init__(table_name="congreso_agenda")

    def scrape_once(self, last_entry, **kwargs) -> ScraperResult:

    def _collect_entry(self, entries: list[CommissionAgendaEntry]):

"""
