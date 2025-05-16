from typing import Optional

from fastapi import Header, HTTPException

from app.core.config import Settings

settings = Settings()
if settings.get_crawler_api_key() == "":
    raise ValueError("CRAWLER_API_KEY environment variable is not set.")

async def get_token_header(token: Optional[str] = Header(None)):
    if token != settings.get_crawler_api_key():
        raise HTTPException(status_code=403)
