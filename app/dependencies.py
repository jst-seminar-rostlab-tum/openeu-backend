import os
from typing import Optional

from fastapi import Header, HTTPException

CRAWLER_API_KEY = os.getenv("CRAWLER_API_KEY")

if not CRAWLER_API_KEY:
    raise RuntimeError("CRAWLER_API_KEY environment variable is not set")


async def get_token_header(token: Optional[str] = Header(None)):
    if token != CRAWLER_API_KEY:
        raise HTTPException(status_code=403)
