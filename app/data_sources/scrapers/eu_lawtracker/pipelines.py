from dotenv import load_dotenv
import os, httpx, logging
from dataclasses import asdict

logger = logging.getLogger(__name__)

load_dotenv()


class SupabasePipeline:
    TABLE  = "laws"
    URL    = os.environ["SUPABASE_URL"] + "/rest/v1/" + TABLE
    HEADERS= {
      "apikey":    os.environ["SUPABASE_KEY"],
      "Authorization": f"Bearer {os.environ['SUPABASE_KEY']}",
      "Content-Type":  "application/json"
    }

    def process_item(self, item, spider):
        rec = asdict(item)
        rec["source"] = spider.name
        sa = rec.get("scraped_at")
        if hasattr(sa, "isoformat"): rec["scraped_at"] = sa.isoformat()
        try:
            httpx.post(self.URL, headers=self.HEADERS, json=[rec], params={"upsert":"true"})
        except Exception:
            logger.exception("Failed to write to Supabase via REST")
        return item
    


""" 

import logging
from dataclasses import asdict
from app.core.supabase_client import supabase

logger = logging.getLogger(__name__)

class SupabasePipeline:
    TABLE_NAME = "laws"

    def process_item(self, item, spider):
        record = asdict(item)
        record["source"] = spider.name
        # normalize datetime
        sa = record.get("scraped_at")
        if hasattr(sa, "isoformat"):
            record["scraped_at"] = sa.isoformat()
        try:
            resp = (
                supabase
                .table(self.TABLE_NAME)
                .insert(record, upsert=True)
                .execute()
            )
            if resp.error:
                logger.error("Supabase insert error: %s", resp.error)
        except Exception:
            logger.exception("Failed to write item to Supabase")
        return item
    

 """

