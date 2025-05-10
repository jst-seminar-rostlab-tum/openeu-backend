import os
from datetime import datetime
from threading import Lock
from typing import Optional

from fastapi import FastAPI, HTTPException, Header

# Track application start time
start_time = datetime.utcnow()

# Counter and lock for thread safety
call_count = 0
lock = Lock()

CRAWLER_API_KEY = os.getenv("CRAWLER_API_KEY")

if not CRAWLER_API_KEY:
    raise RuntimeError("CRAWLER_API_KEY environment variable is not set")
app = FastAPI()


@app.get("/")
async def root() -> object:
    return {"message": "Hello World"}

@app.get("/crawl")
async def dummyCrawl(token: Optional[str] = Header(None)) -> object:
    if CRAWLER_API_KEY != token:
        raise HTTPException(status_code=403, detail="Forbidden")

    global call_count
    with lock:
        call_count += 1
        current_count = call_count
    return {
        "last_deployment": start_time.isoformat() + "Z",
        "calls": current_count
    }
