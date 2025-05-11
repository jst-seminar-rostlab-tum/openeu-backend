from datetime import datetime
from threading import Lock

from fastapi import APIRouter
from fastapi.params import Depends

from app.dependencies import get_token_header

router = APIRouter(
    prefix="/crawler",
    tags=["crawler"],
    responses={404: {"description": "Not found"}},
    dependencies=[Depends(get_token_header)]
)

start_time = datetime.now()

call_count = 0
lock = Lock()

@router.get("/")
async def dummy_crawl() -> dict:
    global call_count
    with lock:
        call_count += 1
        current_count = call_count
    return {
        "last_deployment": start_time.isoformat() + "Z",
        "calls": current_count
    }
