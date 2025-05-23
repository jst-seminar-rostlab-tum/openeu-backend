import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Optional

from app.core.supabase_client import supabase

logger = logging.getLogger(__name__)


class ScraperResult:
    def __init__(self, success: bool, error: Optional[Exception] = None, last_entry: Optional[Any] = None) -> None:
        self.success = success
        self.error = error
        self.last_entry = last_entry

    def __repr__(self):
        return f"<ScraperResult success={self.success} error={self.error} last_entry={self.last_entry}>"


class ScraperBase(ABC):
    def __init__(self, table_name: str, max_retries: int = 3, retry_delay: float = 2.0):
        self.table_name = table_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._last_entry = None

    def scrape(self, **args) -> ScraperResult:
        attempt = 0

        while attempt <= self.max_retries:
            try:
                logger.info(f"Attempt {attempt + 1} for {self.__class__.__name__}")
                result = self.scrape_once(self.last_entry, *args)
                if result.success:
                    return result
                else:
                    logger.warning(f"Scrape attempt {attempt + 1} failed, retrying...")
            except Exception as e:
                logger.exception(f"Exception during scrape attempt {attempt + 1}: {e}")
                result = ScraperResult(success=False, error=e, last_entry=self.last_entry)

            attempt += 1
            if attempt <= self.max_retries:
                time.sleep(self.retry_delay)

        return result  # Last result after retries

    @property
    def last_entry(self) -> Any:
        return self._last_entry

    @last_entry.setter
    def last_entry(self, last_entry: Any):
        self._last_entry = last_entry

    def store_entry(self, entry) -> Optional[ScraperResult]:
        try:
            supabase.table(self.table_name).insert(
                entry,
                upsert=True,
            ).execute()
            return None
        except Exception as e:
            logger.error(f"Error storing entry in Supabase: {e}")
            return ScraperResult(False, e, self.last_entry)

    @abstractmethod
    def scrape_once(self, last_entry: Any, **args) -> ScraperResult:
        """Run a single scraping attempt. Should return ScraperResult."""
        pass
