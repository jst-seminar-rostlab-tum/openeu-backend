import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse

from app.core.supabase_client import supabase
from app.core.vector_search import get_top_k_neighbors
from app.models.meeting import Meeting

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


_START = Query(None, description="Start datetime (ISO8601)")
_END = Query(None, description="End datetime (ISO8601)")


def to_utc_aware(dt: Optional[datetime]) -> Optional[datetime]:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


@router.get("/meetings", response_model=list[Meeting])
def get_meetings(
    limit: int = Query(100, gt=1),
    start: Optional[datetime] = _START,
    end: Optional[datetime] = _END,
    query: Optional[str] = Query(None, description="Search query using semantic similarity"),
    country: Optional[str] = Query(None, description="Filter by country (e.g., 'Austria', 'European Union')")
):
    try:
        start = to_utc_aware(start)
        end = to_utc_aware(end)

        # --- SEMANTIC QUERY CASE ---
        if query:
            neighbors = get_top_k_neighbors(
                query=query,
                allowed_sources={},
                k=limit * 3,
            )

            if not neighbors:
                return JSONResponse(status_code=200, content={"data": []})

            map_table_and_id_to_similarity = {}
            source_tables = []
            source_ids = []
            for neighbor in neighbors:
                source_tables.append(neighbor["source_table"])
                source_ids.append(neighbor["source_id"])
                map_table_and_id_to_similarity[f"{neighbor['source_table']}_{neighbor['source_id']}"] = neighbor[
                    "similarity"]

            params = {
                'source_tables': source_tables,
                'source_ids': source_ids,
                'max_results': limit,
                'start_date': start,
                'end_date': end,
                'country': country,
            }
            match = supabase.rpc('get_meetings_by_source_arrays', params=params).execute()

            results = []
            if match.data:
                for record in match.data:
                    record["similarity"] = map_table_and_id_to_similarity[
                        f"{record['source_table']}_{record['source_id']}"
                    ]

                    results.append(record)

            return JSONResponse(status_code=200, content={"data": results[:limit]})

        # --- DEFAULT QUERY CASE ---
        db_query = supabase.table("v_meetings").select("*")

        if start:
            db_query = db_query.gte("meeting_start_datetime", start.isoformat())
        if end:
            db_query = db_query.lte("meeting_start_datetime", end.isoformat())

        if country:
            db_query = db_query.ilike("location", country)

        result = db_query.order("meeting_start_datetime", desc=True).limit(limit).execute()
        data = result.data

        if not isinstance(data, list):
            raise ValueError("Expected list of records from Supabase")

        return JSONResponse(status_code=200, content={"data": data})

    except Exception as e:
        logger.error("INTERNAL ERROR: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
