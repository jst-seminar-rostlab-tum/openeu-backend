import logging
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from typing import Optional

from app.core.alerts import (
    create_alert,
    get_user_alerts,
    set_alert_active,
    delete_alert,
    find_relevant_meetings,
)
from app.core.supabase_client import supabase

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/alerts")
async def create_alert_endpoint(request: Request):
    caller_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
    try:
        payload = await request.json()
        logger.info("POST /alerts | caller=%s | payload=%s", caller_ip, payload)
        alert = create_alert(**payload)
        return JSONResponse(status_code=201, content={"data": alert})
    except Exception as e:
        logger.error("INTERNAL ERROR (POST /alerts): %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/alerts")
async def get_alerts_endpoint(
    request: Request,
    user_id: str = Query(..., description="User ID for retrieving alerts"),
    include_inactive: Optional[bool] = Query(False, description="Include inactive alerts"),
):
    caller_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
    try:
        logger.info("GET /alerts | caller=%s | user_id=%s | include_inactive=%s", caller_ip, user_id, include_inactive)
        alerts = get_user_alerts(user_id, include_inactive=include_inactive)
        return JSONResponse(status_code=200, content={"data": alerts})
    except Exception as e:
        logger.error("INTERNAL ERROR (GET /alerts): %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.patch("/alerts/{alert_id}")
async def set_alert_active_endpoint(
    alert_id: str,
    active: bool = Query(..., description="Set alert active/inactive"),
):
    try:
        set_alert_active(alert_id, active=active)
        return JSONResponse(status_code=200, content={"status": "success"})
    except Exception as e:
        logger.error("INTERNAL ERROR (PATCH /alerts/%s): %s", alert_id, e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.delete("/alerts/{alert_id}")
async def delete_alert_endpoint(
    alert_id: str,
):
    try:
        delete_alert(alert_id)
        return JSONResponse(status_code=200, content={"status": "deleted"})
    except Exception as e:
        logger.error("INTERNAL ERROR (DELETE /alerts/%s): %s", alert_id, e)
        raise HTTPException(status_code=500, detail=str(e)) from e


# --- Optional: Endpoint to get relevant meetings for an alert ---
@router.get("/alerts/{alert_id}/meetings")
async def get_relevant_meetings_endpoint(alert_id: str, k: int = Query(50)):
    try:
        # This line is correct:
        resp = supabase.table("alerts").select("*").eq("id", alert_id).execute()
        alert = resp.data[0] if resp.data else None
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        # This is the key call:
        meetings = find_relevant_meetings(alert, k=k)
        return JSONResponse(status_code=200, content={"data": meetings})
    except Exception as e:
        logger.error("INTERNAL ERROR (GET /alerts/%s/meetings): %s", alert_id, e)
        raise HTTPException(status_code=500, detail=str(e)) from e
