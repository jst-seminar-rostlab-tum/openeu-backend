import logging
from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List

from app.core.alerts import (
    create_alert,
    get_user_alerts,
    set_alert_active,
    delete_alert,
    find_relevant_meetings_for_alert,
)
from app.core.supabase_client import supabase

logger = logging.getLogger(__name__)
router = APIRouter()


# --- Pydantic models ---
class CreateAlertRequest(BaseModel):
    user_id: str
    description: str

class AlertResponse(BaseModel):
    id: str
    user_id: str
    description: str
    embedding: list[float]
    relevancy_threshold: float
    last_run_at: Optional[str]
    is_active: bool
    created_at: Optional[str]
    updated_at: Optional[str]
    # Add other fields as needed



@router.post("/alerts", response_model=AlertResponse, status_code=201)
async def create_alert_endpoint(alert: CreateAlertRequest, request: Request):
    caller_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
    try:
        logger.info("POST /alerts | caller=%s | payload=%s", caller_ip, alert.dict())
        result = create_alert(
            user_id=alert.user_id,
            description=alert.description
        )
        return result
    except Exception as e:
        logger.error("INTERNAL ERROR (POST /alerts): %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/alerts", response_model=List[AlertResponse])
async def get_alerts_endpoint(
    request: Request,
    user_id: str = Query(..., description="User ID for retrieving alerts"),
    include_inactive: Optional[bool] = Query(False, description="Include inactive alerts"),
):
    caller_ip = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
    try:
        logger.info("GET /alerts | caller=%s | user_id=%s | include_inactive=%s", caller_ip, user_id, include_inactive)
        alerts = get_user_alerts(user_id, include_inactive=include_inactive)
        return alerts
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
        resp = supabase.table("alerts").select("*").eq("id", alert_id).execute()
        alert = resp.data[0] if resp.data else None
        if not alert:
            raise HTTPException(status_code=404, detail="Alert not found")
        meetings = find_relevant_meetings_for_alert(alert, k=k)  # Update if you renamed the function
        return {"data": meetings}
    except Exception as e:
        logger.error("INTERNAL ERROR (GET /alerts/%s/meetings): %s", alert_id, e)
        raise HTTPException(status_code=500, detail=str(e)) from e
