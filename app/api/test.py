from fastapi import APIRouter, HTTPException
from app.core.mail.status_change import notify_status_change
from app.core.supabase_client import supabase
# test purposes doga

router = APIRouter()


@router.post("/test-notify-status-change")
def test_notify_status_change():
    user_id = "00000000-0000-0000-0000-000000000000"

    # Fetch the most recently scraped legislation (or change to a fixed ID)
    try:
        response = (
            supabase.table("legislative_files")
            .select("id, title, status, link, details_link")
            .order("scraped_at", desc=True)
            .limit(1)
            .execute()
        )

        if not response.data:
            raise HTTPException(status_code=404, detail="No legislation found to test")

        legislation = response.data[0]
        old_status = "Initial Status for testing"

        result = notify_status_change(user_id=user_id, legislation=legislation, old_status=old_status)

        if result:
            return {"success": True, "message": f"Test email sent to {user_id}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
