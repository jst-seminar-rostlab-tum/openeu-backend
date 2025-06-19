import logging
import os
from datetime import datetime
from typing import Any

import requests

from app.core.deepl_translator import translator
from app.data_sources.scraper_base import ScraperBase, ScraperResult
from app.data_sources.translator.translator import DeepLTranslator


class BundestagPlenarprotokolleScraper(ScraperBase):
    def __init__(self, max_retries: int = 3, retry_delay: float = 2.0):
        # target table is "bt_plenarprotokolle"
        super().__init__(table_name="bt_plenarprotokolle", max_retries=max_retries, retry_delay=retry_delay)
        self.translator = DeepLTranslator(translator)
        self.API_BASE = "https://search.dip.bundestag.de/api/v1"
        self.API_KEY = os.getenv("BUNDESTAG_KEY")
        self.HEADERS = {"Authorization": f"ApiKey {self.API_KEY}"}

    def scrape_once(self, last_entry: Any, **args) -> ScraperResult:
        """
        Fetch all new plenary protocols between start_date and end_date.
        last_entry may be used to resume from a cursor if desired.
        """
        try:
            start_dt = datetime.fromisoformat(str(args.get("start_date")))
            end_dt = datetime.fromisoformat(str(args.get("end_date")))

            page = 1
            size = 50
            cursor = None

            while True:
                # 1) Fetch metadata page
                params: dict[str, Any] = {
                    "page": page,
                    "size": size,
                    "f.datum.start": start_dt.strftime("%Y-%m-%d"),
                    "f.datum.end": end_dt.strftime("%Y-%m-%d"),
                }
                if cursor is not None:
                    params["cursor"] = cursor

                resp = requests.get(f"{self.API_BASE}/plenarprotokoll", headers=self.HEADERS, params=params)
                resp.raise_for_status()
                data = resp.json()

                docs = data.get("documents", [])
                if not docs:
                    break

                for item in docs:
                    pid = item["id"]
                    datum = item.get("datum")
                    if not datum:
                        continue

                    # fetch full text
                    text_json = requests.get(f"{self.API_BASE}/plenarprotokoll-text/{pid}", headers=self.HEADERS).json()

                    record = {
                        "id": pid,
                        "datum": datum,
                        "titel": item.get("titel"),
                        "sitzungsbemerkung": item.get("sitzungsbemerkung") or None,
                        "text": text_json.get("text", ""),
                    }

                    try:
                        record["title_english"] = str(self.translator.translate(record["titel"] or ""))
                    except Exception as e:
                        logging.error(f"Translation failed for {pid}: {e}")
                        record["title_english"] = "Not available"

                    store_err = self.store_entry(record, embedd_entries=False)
                    if store_err:
                        return store_err

                    
                    self.embedding_generator.embed_row(
                        source_table=self.table_name,
                        row_id=pid,
                        content_column="text",
                        content_text=(record["text"] + record["datum"]),
                    )

                self.last_entry = pid
                raw_cursor = data.get("cursor")
                if isinstance(raw_cursor, int):
                    cursor = raw_cursor
                    page += 1
                else:
                    break

            return ScraperResult(success=True, last_entry=self.last_entry)

        except Exception as e:
            logging.exception("Error in scrape_once")
            return ScraperResult(success=False, error=e, last_entry=self.last_entry)
