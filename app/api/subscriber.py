from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.core.auth import get_current_user
from app.core.supabase_client import supabase

router = APIRouter()


class SubscribeRequest(BaseModel):
    legislation_id: str


class Subscription(BaseModel):
    id: str
    user_id: str
    legislation_id: str
    created_at: str


@router.post("/subscribe")
def subscribe_to_legislation(request: Request, req: SubscribeRequest):
    user = get_current_user(request)
    try:
        supabase.table("subscriptions").insert({"user_id": user.id, "legislation_id": req.legislation_id}).execute()

        return {"success": True, "message": "Subscribed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/unsubscribe")
def unsubscribe_from_legislation(request: Request, req: SubscribeRequest):
    user = get_current_user(request)
    try:
        result = (
            supabase.table("subscriptions")
            .delete()
            .eq("user_id", user.id)
            .eq("legislation_id", req.legislation_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Subscription not found")

        return {"success": True, "message": "Unsubscribed successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/subscriptions")
def get_user_subscriptions(request: Request) -> list[Subscription]:
    user = get_current_user(request)
    try:
        result = supabase.table("subscriptions").select().eq("user_id", user.id).execute()

        return [Subscription(**item) for item in result.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
