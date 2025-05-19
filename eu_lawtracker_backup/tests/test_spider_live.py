
#pytest -m "integration" -q
# pytest -m "integration" -q --tb=short

# tests/test_spider_live.py
from scrapy.crawler import CrawlerProcess
from eu_lawtracker.backup_code.lawtracker_backup import LawTrackerSpider
from eu_lawtracker.models import Law, Topic, topic_laws
from sqlalchemy.orm import Session
from sqlalchemy import select
import sqlalchemy as sa, pytest, os

@pytest.mark.integration
def test_crawl_one_topic(pg_url):
    # ── run spider on just the first topic to keep it short
    process = CrawlerProcess(settings={
        "DATABASE_URL": pg_url,
        "DOWNLOAD_DELAY": 1.0,
        "CLOSESPIDER_PAGECOUNT": 15,   # stop early
    })
    process.crawl(LawTrackerSpider, start_urls=[
        "https://law-tracker.europa.eu/results?eurovoc=[%2216_DOM%22]&searchType=topics&page=0&pageSize=10&lang=en"
    ])
    process.start()
    # ── assert DB got rows
    eng = sa.create_engine(pg_url.replace("+psycopg2", ""))
    with eng.begin() as conn:
        cnt = conn.scalar(sa.text("SELECT count(*) FROM laws"))
        assert cnt > 0



