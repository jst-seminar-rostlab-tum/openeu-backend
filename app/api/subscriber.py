from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.core.auth import check_request_user_id
from app.core.supabase_client import supabase

router = APIRouter()


class SubscribeRequest(BaseModel):
    user_id: str
    legislation_id: str


@router.post("/subscribe")
def subscribe_to_legislation(request: Request, req: SubscribeRequest):
    check_request_user_id(request, req.user_id)
    try:
        supabase.table("subscriptions").insert({"user_id": req.user_id, "legislation_id": req.legislation_id}).execute()

        return {"success": True, "message": "Subscribed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
