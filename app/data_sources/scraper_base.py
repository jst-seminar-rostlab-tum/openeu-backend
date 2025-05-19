import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Optional

logger = logging.getLogger(__name__)

class ScraperResult:
    def __init__(self, success: bool, data: Any = None, error: Optional[Exception] = None):
        self.success = success
        self.data = data
        self.error = error

    def __repr__(self):
        return f"<ScraperResult success={self.success} data={self.data} error={self.error}>"

class ScraperBase(ABC):
    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    def scrape(self) -> ScraperResult:
        attempt = 0
        last_entry = None

        while attempt <= self.max_retries:
            try:
                logger.info(f"Attempt {attempt+1} for {self.__class__.__name__}")
                result = self.scrape_once(last_entry)
                if result.success:
                    return result
                else:
                    logger.warning(f"Scrape attempt {attempt+1} failed, retrying...")
            except Exception as e:
                logger.exception(f"Exception during scrape attempt {attempt+1}: {e}")
                result = ScraperResult(success=False, error=e)

            last_entry = self.get_last_entry()
            attempt += 1
            if attempt <= self.max_retries:
                time.sleep(self.retry_delay)

        return result  # Last result after retries

    @abstractmethod
    def scrape_once(self, last_entry: Any) -> ScraperResult:
        """Run a single scraping attempt. Should return ScraperResult."""
        pass

    @abstractmethod
    def get_last_entry(self) -> Any:
        """Return last successful entry or state needed to retry."""
        pass