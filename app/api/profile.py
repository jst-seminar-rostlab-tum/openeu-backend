import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.openai_client import EMBED_MODEL, openai
from app.core.supabase_client import supabase
from app.models.profile import ProfileCreate

router = APIRouter(prefix="/profile", tags=["profile"])


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_profile(profile: ProfileCreate):
    """
    Create or update a user profile: compute embedding from company_name, company_description, and topic_list,
    then upsert the record into Supabase.
    """
    # Build input text for embedding
    combined = (
        f"{profile.company_name}. {profile.company_description}."
        + f" Topics: {', '.join(profile.topic_list)}"
        + f" Countries: {', '.join(profile.countries)}"
    )

    # Generate embedding
    try:
        logger.info("Requesting embedding from OpenAI for profile %s", profile.id)
        resp = openai.embeddings.create(input=[combined], model=EMBED_MODEL)
        embedding = resp.data[0].embedding
        logger.info("Received embedding for profile %s", profile.id)
    except Exception as e:
        logger.error("Embedding generation failed for profile %s: %s", profile.id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Embedding generation failed"
        ) from e

    # Upsert into Supabase
    payload = profile.model_dump()

    payload["id"] = str(payload["id"])
    payload["embedding"] = embedding

    countries = payload.pop("countries")
    topic_list = payload["topic_list"]

    try:
        supabase.table("profiles").upsert(payload).execute()
        logger.info("Successfully upserted profile %s", payload["id"])

        if topic_list:
            # Clear existing topic associations for the profile
            supabase.table("profiles_to_topics").delete().match({"profile_id": payload["id"]}).execute()
            # Insert new topic associations
            topic_rows = [{"profile_id": payload["id"], "topic_id": topic} for topic in topic_list]
            supabase.table("profiles_to_topics").insert(topic_rows).execute()

        if countries:
            # Clear existing country associations for the profile
            supabase.table("profiles_to_countries").delete().match({"profile_id": payload["id"]}).execute()
            # Insert new country associations
            country_rows = [{"profile_id": payload["id"], "country": country} for country in countries]
            supabase.table("profiles_to_countries").insert(country_rows).execute()

        logger.info("Linked %d topics and %d countries for profile %s", len(topic_list), len(countries), payload["id"])
    except Exception as e:
        logger.error("Supabase upsert failed for profile %s: %s", payload["id"], e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Supabase upsert failed") from e

    return JSONResponse(status_code=status.HTTP_201_CREATED, content={"status": "created"})
