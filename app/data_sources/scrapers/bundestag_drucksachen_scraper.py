import logging
import os
from datetime import datetime
import multiprocessing
from typing import Any, Optional

import requests

from app.core.deepl_translator import translator
from app.data_sources.scraper_base import ScraperBase, ScraperResult
from app.data_sources.translator.translator import DeepLTranslator
from scripts.embedding_generator import embed_row


class BundestagDrucksachenScraper(ScraperBase):
    def __init__(
        self,
        stop_event: multiprocessing.synchronize.Event,
        table_name: str = "bt_documents",
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        super().__init__(table_name, stop_event, max_retries, retry_delay)
        self.translator = DeepLTranslator(translator)
        self.API_BASE = "https://search.dip.bundestag.de/api/v1"
        self.API_KEY = os.getenv("BUNDESTAG_KEY")
        self.HEADERS = {"Authorization": f"ApiKey {self.API_KEY}"}

    def scrape_once(self, last_entry: Any, **args) -> ScraperResult:
        try:
            start_dt = datetime.fromisoformat(str(args.get("start_date")))
            end_dt = datetime.fromisoformat(str(args.get("end_date")))

            cursor: Optional[int] = None
            last_pid: Optional[int] = None

            page = 1
            size = 50

            while True:
                if self.stop_event.is_set():
                    return ScraperResult(
                        success=False,
                        error=Exception(f"Scrape stopped by external stop event; on page {page}"),
                        last_entry=self.last_entry,
                    )

                params: dict[str, Any] = {
                    "page": page,
                    "size": size,
                    "f.datum.start": start_dt.strftime("%Y-%m-%d"),
                    "f.datum.end": end_dt.strftime("%Y-%m-%d"),
                }
                if cursor is not None:
                    params["cursor"] = cursor

                resp = requests.get(f"{self.API_BASE}/drucksache", headers=self.HEADERS, params=params)

                resp.raise_for_status()
                data = resp.json()

                items = data.get("documents", [])
                if not items:
                    logging.info("No more documents to process.")
                    break

                for item in items:
                    pid = item.get("id")
                    datum = item.get("datum")
                    if not pid or not datum:
                        continue

                    record = {
                        "id": pid,
                        "datum": datum,
                        "titel": item.get("titel"),
                        "drucksachetyp": item.get("drucksachetyp") or None,
                    }
                    text_json = requests.get(f"{self.API_BASE}/drucksache-text/{pid}", headers=self.HEADERS).json()

                    record["text"] = text_json.get("text", "")

                    try:
                        record["title_english"] = str(self.translator.translate(record["titel"] or ""))
                    except Exception as e:
                        logging.error(f"Translation failed for {pid}: {e}")
                        record["title_english"] = "Not available"

                    # store and embed
                    store_err = self.store_entry(record, embedd_entries=False)
                    if store_err:
                        return store_err

                    embed_row(
                        source_table=self.table_name,
                        row_id=pid,
                        content_column="title_english",
                        content_text=(record["title_english"] + record["datum"]),
                    )
                    embed_row(
                        source_table=self.table_name,
                        row_id=pid,
                        content_column="text",
                        content_text=record["text"],
                    )

                    last_pid = pid

                raw_cursor = data.get("cursor")
                cursor = raw_cursor if isinstance(raw_cursor, int) else None
                if cursor is None:
                    break
                page += 1

            self.last_entry = last_pid
            return ScraperResult(True, last_entry=last_pid)

        except Exception as e:
            logging.exception(f"Error in scrape_once: {e}")
            return ScraperResult(False, error=e, last_entry=self.last_entry)
