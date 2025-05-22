from datetime import datetime, timedelta
from typing import Optional, List

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import JSONResponse

from dateutil.relativedelta import relativedelta   

from app.models.meeting import Meeting
from app.core.supabase_client import supabase

router = APIRouter()

@router.get("/meetings")
def get_meetings(limit: int = 20):
    try:
        result = supabase \
            .table("v_meetings") \
            .select("*") \
            .order("meeting_start_datetime", desc=True) \
            .limit(limit) \
            .execute()
        
        data = result.data  

        if not isinstance(data, list):
            raise ValueError("Expected list of records from Supabase")

        return JSONResponse(status_code=200, content={"data": data})

    except Exception as e:
        print("INTERNAL ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))