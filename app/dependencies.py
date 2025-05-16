import os
from typing import Optional

from dotenv import find_dotenv, load_dotenv
from fastapi import Header, HTTPException

from app.core.config import Settings

settings = Settings()

async def get_token_header(token: Optional[str] = Header(None)):
    if token != settings.get_crawler_api_key():
        raise HTTPException(status_code=403)
