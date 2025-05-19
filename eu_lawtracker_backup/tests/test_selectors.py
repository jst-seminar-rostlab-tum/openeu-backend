#pytest -q

# tests/test_selectors.py
import pathlib
from scrapy.http import HtmlResponse, Request
from eu_lawtracker.backup_code.lawtracker_backup import LawTrackerSpider

FIXTURES = pathlib.Path(__file__).with_suffix("")

def html(name: str) -> HtmlResponse:
    body = (FIXTURES / name).read_text(encoding="utf-8")
    return HtmlResponse(
        url="https://example.com", request=Request("GET", "x"), body=body, encoding="utf-8"
    )

def test_parse_search_extracts_10_items():
    spider = LawTrackerSpider()
    res = html("search_economics.html")
    items = list(spider.parse_search(res))
    assert len([i for i in items if hasattr(i, "procedure_id")]) == 10

def test_parse_detail_gets_summary():
    spider = LawTrackerSpider()
    res = html("detail_2025_0090.html")
    item = list(spider.parse_detail(res))[0]
    assert item.summary.startswith("Proposal for a Regulation")




