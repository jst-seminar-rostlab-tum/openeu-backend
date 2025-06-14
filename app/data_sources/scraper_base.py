import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from postgrest import APIResponse
from zoneinfo import ZoneInfo

from app.core.supabase_client import supabase
from scripts.embedding_generator import embed_row
from app.core.mail.notify_job_failure import notify_job_failure

logger = logging.getLogger(__name__)

brussels_tz = ZoneInfo("Europe/Brussels")


class ScraperResult:
    def __init__(
        self, success: bool, lines_added: int = 0, error: Optional[Exception] = None, last_entry: Optional[Any] = None
    ) -> None:
        self.success = success
        self.lines_added = lines_added
        self.error = error
        self.last_entry = last_entry

    def __repr__(self):
        return f"<ScraperResult success={self.success} error={self.error} last_entry={self.last_entry}>"


class ScraperBase(ABC):
    def __init__(self, table_name: str, max_retries: int = 1, retry_delay: float = 2.0):
        self.table_name = table_name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.lines_added = 0
        self._last_entry = None

    def scrape(self, **args) -> ScraperResult:
        attempt = 0

        while attempt <= self.max_retries:
            try:
                logger.info(f"Attempt {attempt + 1} for {self.__class__.__name__}")
                result = self.scrape_once(self.last_entry, **args)
                if result.success:
                    return result
                else:
                    logger.warning(f"Scrape attempt {attempt + 1} failed, retrying...")
                    if result.error:
                        job_name = f"{self.__class__.__name__}"

                        notify_job_failure(job_name, result.error)
                        logger.error(f"Error: {result.error.__class__} - {result.error}")
            except Exception as e:
                logger.exception(f"Exception during scrape attempt {attempt + 1}: {e}")
                result = ScraperResult(success=False, error=e, last_entry=self.last_entry)

            attempt += 1
            if attempt <= self.max_retries:
                time.sleep(self.retry_delay)

        result.lines_added = self.lines_added
        return result  # Last result after retries

    @property
    def last_entry(self) -> Any:
        return self._last_entry

    @last_entry.setter
    def last_entry(self, last_entry: Any):
        self._last_entry = last_entry

    def embedd_entries(self, response: APIResponse) -> None:
        ids_and_inputs = [(row.get("id"), row.get("embedding_input")) for row in response.data] if response.data else []
        for source_id, embedding_input in ids_and_inputs:
            if source_id and embedding_input:
                embed_row(
                    source_table=self.table_name,
                    row_id=source_id,
                    content_column="embedding_input",
                    content_text=embedding_input,
                )

    def store_entry(
        self, entry, on_conflict: Optional[str] = None, embedd_entries: bool = True
    ) -> Optional[ScraperResult]:
        try:
            # add/update scraped_at timestamp
            entry["scraped_at"] = datetime.now(brussels_tz).isoformat()
            response = supabase.table(self.table_name).upsert(entry, on_conflict=on_conflict).execute()
            if embedd_entries:
                self.embedd_entries(response)
            self.lines_added += len(response.data) if response.data else 0
            return None
        except Exception as e:
            logger.error(f"Error storing entry in Supabase: {e}")
            return ScraperResult(False, self.lines_added, e, self.last_entry)

    def store_entry_returning_id(self, entry: Any, on_conflict: Optional[str] = None) -> Optional[str]:
        """
        Store an entry in the database and return the ID of the stored entry.
        """
        try:
            response = supabase.table(self.table_name).upsert(entry, on_conflict=on_conflict).execute()
            self.lines_added += 1
            return response.data[0].get("id") if response.data else None
        except Exception as e:
            logger.error(f"Error storing entry in Supabase: {e}")
            return None

    @abstractmethod
    def scrape_once(self, last_entry: Any, **args) -> ScraperResult:
        """Run a single scraping attempt. Should return ScraperResult."""
        pass
