import os
import requests
from time import sleep
from datetime import datetime
from openeu_backend.app.core.supabase_client import supabase
from postgrest.exceptions import APIError
from typing import Optional, Dict, Any
import logging

logging.basicConfig(level=logging.INFO)

API_BASE = "https://search.dip.bundestag.de/api/v1"
API_KEY = os.getenv("BUNDESTAG_KEY")  
headers  = {"Authorization": f"ApiKey {API_KEY}"}

def fetch_plenarprotokolle(
    page: int = 1,
    size: int = 100,
    cursor: Optional[str] = None,
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """
    Fetch a page of plenary-protocol metadata, optionally filtered by update timestamps.
    """
    params = {"page": page, "size": size}
    if cursor:
        params["cursor"] = cursor
    
    params["f.datum.start"] = start_date.strftime("%Y-%m-%d")
     
    params["f.datum.end"] = end_date.strftime("%Y-%m-%d")

    resp = requests.get(f"{API_BASE}/plenarprotokoll", headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()


def fetch_protocol_text(protocol_id: str) -> Dict[str, Any]:
    
    resp = requests.get(f"{API_BASE}/plenarprotokoll-text/{protocol_id}", headers=headers)
    resp.raise_for_status()
    return resp.json()


def upsert_record(record: Dict[str, Any]) -> None:
    
    try:
        resp = supabase.table("plenarprotokolle") \
                       .upsert(record) \
                       .execute()
        logging.info(f"Upserted {record['id']}")
    except APIError as e:
        logging.error(f"Supabase APIError: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during upsert for {record.get('id', '?')}: {e}")

def in_date_range(datum_str: str, start: datetime, end: datetime) -> bool:
    
    try:
        d = datetime.fromisoformat(datum_str).date()
    except ValueError:
        logging.warning(f"Invalid date format: {datum_str}")
        return False
    return start.date() <= d <= end.date()

def scrape_bundestag_plenarprotokolle(start_date: str, end_date: str) -> None:
    
    start = datetime.fromisoformat(start_date)
    end   = datetime.fromisoformat(end_date)

    page, size, cursor = 1, 50, None

    while True:
        data = fetch_plenarprotokolle(page, size, cursor, start_date=start,end_date=end)
        items = data.get("documents", [])
        if not items:
            logging.info("Finished: no more documents.")
            break

        for item in items:
            pid = item["id"]
            datum_str = item.get("datum")
            if not datum_str or not in_date_range(datum_str, start, end):
                continue

            meta = {
                "id": pid,
                "datum": datum_str,
                "titel": item.get("titel"),
                "sitzungsbemerkung": item.get("sitzungsbemerkung") or None,
            }

            text_json = fetch_protocol_text(pid)
            meta["text"] = text_json.get("text", "")

            upsert_record(meta)
            sleep(0.1)

        cursor = data.get("cursor")
        page += 1
