from app.data_sources.apis.source1_api import Source1
from app.data_sources.scrapers.site1_scraper import Site1


class TaskRunner:
    def __init__(self) -> None:
        Source1()
        Site1()
