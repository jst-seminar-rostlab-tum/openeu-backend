import logging
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse

from app.core.auth import check_request_user_id
from app.core.supabase_client import supabase
from app.models.notifications import Notification

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"],
)


@router.get("/{user_id}", response_model=list[Notification])
def get_notifications_for_user(
    request: Request,
    user_id: UUID,
    limit: int = Query(100, gt=0),
):
    check_request_user_id(request, str(user_id))
    """
    Retrieve all notifications for a specific user by their ID.
    """
    try:
        result = (
            supabase.table("notifications")
            .select("*")
            .eq("user_id", str(user_id))
            .order("sent_at", desc=True)
            .limit(limit)
            .execute()
        )
        data = result.data

        if not isinstance(data, list):
            raise ValueError("Expected list of records from Supabase")

        return JSONResponse(status_code=200, content={"data": data})

    except Exception as e:
        logger.error("INTERNAL ERROR: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
