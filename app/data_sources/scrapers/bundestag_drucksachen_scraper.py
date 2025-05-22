import logging
from datetime import datetime
from time import sleep
from typing import Optional

from app.data_sources.scrapers.bundestag_plenarprotocol_scaper import (
    fetch_plenarprotokolle,
    fetch_protocol_text,
    upsert_record,
)


def scrape_bundestag_drucksachen(start_date: str, end_date: str) -> None:
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    page: int = 1
    size: int = 50
    cursor: Optional[int] = None

    while True:
        data = fetch_plenarprotokolle(
            endpoint="drucksache", page=page, size=size, cursor=cursor, start_date=start, end_date=end
        )
        items = data.get("documents", [])
        if not items:
            logging.info("Finished: no more documents.")
            break

        for item in items:
            pid = item["id"]
            datum_str = item.get("datum")
            if not datum_str:
                continue

            meta = {
                "id": pid,
                "datum": datum_str,
                "titel": item.get("titel"),
                "drucksachetyp": item.get("drucksachetyp") or None,
            }

            text_json = fetch_protocol_text(pid, endpoint="drucksache-text")
            meta["text"] = text_json.get("text", "")

            upsert_record(meta, "bt_documents")
            sleep(0.1)

        raw_cursor = data.get("cursor")
        cursor = raw_cursor if isinstance(raw_cursor, int) else None
        page += 1
