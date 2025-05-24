import logging
import os
from datetime import datetime
from time import sleep
from typing import Any, Optional, Union

import requests
from postgrest.exceptions import APIError

from app.core.deepl_translator import translator
from app.core.supabase_client import supabase
from app.data_sources.translator.translator import DeepLTranslator
from scripts.embedding_generator import embed_row

API_BASE = "https://search.dip.bundestag.de/api/v1"
API_KEY = os.getenv("BUNDESTAG_KEY")
headers = {"Authorization": f"ApiKey {API_KEY}"}
translator = DeepLTranslator(translator)

# Type aliases:
QueryParamValue = Union[str, int, float, None]


def fetch_plenarprotokolle(
    endpoint: str,
    page: int = 1,
    size: int = 100,
    cursor: Optional[int] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
) -> dict[str, Any]:
    """
    Fetch a page of plenary-protocol metadata, optionally filtered by update timestamps.
    """
    params: dict[str, QueryParamValue] = {
        "page": page,
        "size": size,
        "f.datum.start": "",
        "f.datum.end": "",
    }
    if cursor:
        params["cursor"] = cursor

    if start_date:
        params["f.datum.start"] = start_date.strftime("%Y-%m-%d")

    if end_date:
        params["f.datum.end"] = end_date.strftime("%Y-%m-%d")

    resp = requests.get(f"{API_BASE}/{endpoint}", headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()


def fetch_protocol_text(
    protocol_id: str,
    endpoint: str,
) -> dict[str, Any]:
    resp = requests.get(f"{API_BASE}/{endpoint}/{protocol_id}", headers=headers)
    resp.raise_for_status()
    return resp.json()


def upsert_record(record: dict[str, Any], table: str) -> None:
    try:
        supabase.table(table).upsert(record).execute()
        logging.info(f"Upserted {record['id']}")
    except APIError as e:
        logging.error(f"Supabase APIError: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during upsert for {record.get('id', '?')}: {e}")


def scrape_bundestag_plenarprotokolle(start_date: str, end_date: str) -> None:
    start = datetime.fromisoformat(start_date)
    end = datetime.fromisoformat(end_date)

    page: int = 1
    size: int = 50
    cursor: Optional[int] = None

    while True:
        data = fetch_plenarprotokolle(
            endpoint="plenarprotokoll", page=page, size=size, cursor=cursor, start_date=start, end_date=end
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
                "sitzungsbemerkung": item.get("sitzungsbemerkung") or None,
            }

            text_json = fetch_protocol_text(pid, endpoint="plenarprotokoll-text")
            meta["text"] = text_json.get("text", "")

            title_english = str(translator.translate(item.get("titel"))) if item.get("titel") else ""

            text_english = str(translator.translate(meta["text"])) if meta["text"] else ""

            meta["title_english"] = title_english
            meta["text_english"] = text_english

            upsert_record(meta, "bt_plenarprotokolle")
            embed_row(
                source_table="bt_plenarprotokolle",
                row_id=pid,
                content_column="title_english",
                content_text=meta["title_english"],
            )
            embed_row(
                source_table="bt_plenarprotokolle",
                row_id=pid,
                content_column="text_english",
                content_text=meta["text_english"],
            )

            sleep(0.1)

        raw_cursor = data.get("cursor")
        cursor = raw_cursor if isinstance(raw_cursor, int) else None
        if cursor is None:
            logging.info("Finished: no more documents.")
            break
        page += 1
