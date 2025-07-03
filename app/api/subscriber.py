from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.supabase_client import supabase

router = APIRouter()


class SubscribeRequest(BaseModel):
    user_id: str
    legislation_id: str


@router.post("/subscribe")
def subscribe_to_legislation(req: SubscribeRequest):
    try:
        response = (
            supabase.table("subscriptions")
            .insert({"user_id": req.user_id, "legislation_id": req.legislation_id})
            .execute()
        )

        if response.error:
            raise HTTPException(status_code=400, detail=str(response.error))

        return {"success": True, "message": "Subscribed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
