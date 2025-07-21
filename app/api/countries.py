import logging

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi_cache.decorator import cache

from app.core.supabase_client import supabase

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/countries", response_model=dict[str, list[str]])
@cache(namespace="countries", expire=86400)
def get_countries():
    try:
        response = supabase.rpc("get_countries").execute()
        countries = response.data
        if "European Union" in countries:
            countries.remove("European Union")
            countries.insert(0, "European Union")
        return JSONResponse(status_code=200, content={"data": countries})
    except Exception as e:
        logger.error("INTERNAL ERROR: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
