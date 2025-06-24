import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.openai_client import EMBED_MODEL, openai
from app.core.supabase_client import supabase
from app.core.vector_search import get_top_k_neighbors

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


"""Core helper functions for the Smart‑Alerts feature.

Responsibilities handled here:
  * Generate and store embeddings for user‑defined alert prompts.
  * CRUD helpers for the `alerts` table.
  * Utility to fetch the subset of alerts that are due for processing.
  * Matching logic that returns relevant meetings for a given alert using the
    existing `vector_search.get_top_k_neighbors` helper.
  * Convenience wrappers for marking an alert as processed / pausing / etc.

This file deliberately mirrors the API style already used in
`app/core/relevant_meetings.py` to minimise cognitive overhead.
"""

# ---------------------------------------------------------------------------
# Embeddings helpers
# ---------------------------------------------------------------------------


def _utc_now() -> datetime:
    """Return the current moment as a timezone‑aware UTC datetime."""
    return datetime.now(timezone.utc)


def build_embedding(text: str) -> list[float]:
    """Create an embedding for *text*, injecting current‑date context.

    Parameters
    ----------
    text : str
        Natural‑language description coming from the user (e.g. "I want all
        new meetings about sustainability").

    Returns
    -------
    list[float]
        1536‑dimensional vector produced by the OpenAI embedding endpoint.
    """
    date_ctx = _utc_now().strftime("%Y‑%m‑%d")
    prompt = f"{text}\nCurrent date: {date_ctx}"

    resp = openai.embeddings.create(input=prompt, model=EMBED_MODEL)
    emb: list[float] = resp.data[0].embedding  # type: ignore[attr-defined]
    return emb


# ---------------------------------------------------------------------------
# Alerts CRUD helpers
# ---------------------------------------------------------------------------


def create_alert(
    *,
    user_id: str,
    description: str,
    frequency: str = "daily",
    relevancy_threshold: float = 0.75,
) -> dict:
    """Insert a new record into the *alerts* table and return it."""
    emb = build_embedding(description)

    payload = {
        "user_id": user_id,
        "description": description,
        "embedding": emb,
        "frequency": frequency,
        "relevancy_threshold": relevancy_threshold,
    }
    resp = supabase.table("alerts").insert(payload).execute()
    if hasattr(resp, "error") and resp.error:
        raise RuntimeError(f"Supabase error while inserting alert: {resp.error}")

    rows = resp.data or []
    if not rows:
        raise RuntimeError("No alert returned after insert")
    alert = rows[0]  # inserted row

    logger.info("Created alert %s for user %s", alert.get("id"), user_id)
    return alert


def get_user_alerts(user_id: str, *, include_inactive: Optional[bool] = None,) -> list[dict]:
    """Return alerts belonging to *user_id* (active by default)."""
    query = supabase.table("alerts").select("*").eq("user_id", user_id)
    if not include_inactive:
        query = query.eq("is_active", True)
    resp = query.execute()
    return resp.data or []


# ---------------------------------------------------------------------------
# Scheduler utilities
# ---------------------------------------------------------------------------

_FREQUENCY_TO_DELTA = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
    "monthly": timedelta(days=30),  # coarse approximation
}


def fetch_due_alerts(now: datetime | None = None) -> list[dict]:
    """Return all *active* alerts whose *last_run_at* is older than their
    configured frequency (or has never run)."""
    if now is None:
        now = _utc_now()

    # Fetch in two steps because Supabase RPC/SQL is limited when mixing
    # intervals; filtering in Python is acceptable for our small alert counts.
    resp = supabase.table("alerts").select("*").eq("is_active", True).execute()
    alerts: list[dict] = resp.data or []

    due: list[dict] = []
    for alert in alerts:
        freq = alert.get("frequency", "daily")
        delta = _FREQUENCY_TO_DELTA.get(freq, timedelta(days=1))
        last_run: str | None = alert.get("last_run_at")
        if last_run is None:
            due.append(alert)
            continue
        last_dt = datetime.fromisoformat(last_run.replace("Z", "+00:00"))
        if now - last_dt >= delta:
            due.append(alert)
    return due


def mark_alert_ran(alert_id: str, *, ran_at: datetime | None = None) -> None:
    """Update *last_run_at* to *ran_at* (defaults to now) for the given alert."""
    if ran_at is None:
        ran_at = _utc_now()
    supabase.table("alerts").update({"last_run_at": ran_at.isoformat()}).eq("id", alert_id).execute()


# ---------------------------------------------------------------------------
# Matching logic to retrieve relevant meetings
# ---------------------------------------------------------------------------


def find_relevant_meetings(alert: dict, *, k: int = 50) -> list[dict]:
    """Run a vector search for meetings that match *alert* and pass its threshold.

    Duplicates that were already sent via *alert_notifications* are filtered
    out so a given user only ever receives a meeting once per alert.
    """
    neighbors = get_top_k_neighbors(
        embedding=alert["embedding"],
        k=k,
        sources=["meeting_embeddings"],
    )
    if not neighbors:
        return []

    # Apply threshold early to reduce DB hits later.
    sim_threshold = alert["relevancy_threshold"]
    filtered = [n for n in neighbors if n["similarity"] >= sim_threshold]
    if not filtered:
        return []

    meeting_ids = [n["source_id"] for n in filtered]

    # Exclude meetings that have already been sent for this alert
    already_sent_resp = (
        supabase.table("alert_notifications")
        .select("meeting_id")
        .eq("alert_id", alert["id"])
        .in_("meeting_id", meeting_ids)
        .execute()
    )
    sent_ids = {row["meeting_id"] for row in (already_sent_resp.data or [])}

    remaining_ids = [mid for mid in meeting_ids if mid not in sent_ids]
    if not remaining_ids:
        return []

    # Fetch meeting records from the materialised view – same as /meetings uses
    meetings_resp = supabase.table("v_meetings").select("*").in_("source_id", remaining_ids).execute()

    # Merge similarity back onto rows for convenience
    sim_map = {n["source_id"]: n["similarity"] for n in filtered}
    meetings: list[dict] = meetings_resp.data or []
    for m in meetings:
        m["similarity"] = sim_map.get(m["meeting_id"], 0.0)
    # sort by similarity desc so the email template can just iterate
    meetings.sort(key=lambda m: m["similarity"], reverse=True)
    return meetings


# ---------------------------------------------------------------------------
# Public façade – single call that the cron job will use
# ---------------------------------------------------------------------------


def process_alert(alert: dict) -> list[dict]:
    """Wrapper that returns *new* meeting items for an alert and records that
    they were sent (but **does not** send the email itself).

    The calling job is responsible for actually dispatching the email and
    writing to the user‑visible `notifications` table.
    """
    meetings = find_relevant_meetings(alert)
    if not meetings:
        mark_alert_ran(alert["id"])
        return []

    # Log to alert_notifications so we don't re‑send next time
    supabase.table("alert_notifications").insert(
        [
            {
                "alert_id": alert["id"],
                "meeting_id": m["meeting_id"],
                "similarity": m["similarity"],
            }
            for m in meetings
        ]
    ).execute()

    mark_alert_ran(alert["id"])
    logger.info(
        "Alert %s matched %d new meeting(s) for user %s",
        alert["id"],
        len(meetings),
        alert["user_id"],
    )
    return meetings


# ---------------------------------------------------------------------------
# Convenience toggles – pause / resume / delete
# ---------------------------------------------------------------------------


def set_alert_active(alert_id: str, *, active: bool) -> None:
    supabase.table("alerts").update({"is_active": active}).eq("id", alert_id).execute()


def delete_alert(alert_id: str) -> None:
    supabase.table("alerts").delete().eq("id", alert_id).execute()
