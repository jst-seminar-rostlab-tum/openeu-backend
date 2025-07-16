from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from app.core.auth import check_request_user_id
from app.core.supabase_client import supabase

router = APIRouter()


class SubscribeRequest(BaseModel):
    user_id: str
    legislation_id: str


class GetSubscriptionsRequest(BaseModel):
    user_id: str


class Subscription(BaseModel):
    id: str
    user_id: str
    legislation_id: str
    created_at: str


class SubscriptionResponse(BaseModel):
    success: bool
    message: str


@router.post("/subscribe", response_model=SubscriptionResponse)
def subscribe_to_legislation(request: Request, req: SubscribeRequest) -> SubscriptionResponse:
    check_request_user_id(request, req.user_id)
    try:
        supabase.table("subscriptions").insert({"user_id": req.user_id, "legislation_id": req.legislation_id}).execute()

        return SubscriptionResponse(success=True, message="Subscribed successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/unsubscribe", response_model=SubscriptionResponse)
def unsubscribe_from_legislation(request: Request, req: SubscribeRequest) -> SubscriptionResponse:
    check_request_user_id(request, req.user_id)
    try:
        result = (
            supabase.table("subscriptions")
            .delete()
            .eq("user_id", req.user_id)
            .eq("legislation_id", req.legislation_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Subscription not found")

        return SubscriptionResponse(success=True, message="Unsubscribed successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/subscriptions/{user_id}", response_model=list[Subscription])
def get_user_subscriptions(request: Request, user_id: str) -> list[Subscription]:
    check_request_user_id(request, user_id)
    try:
        result = supabase.table("subscriptions").select().eq("user_id", user_id).execute()

        return [Subscription(**item) for item in result.data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
