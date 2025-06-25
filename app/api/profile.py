import logging
from types import SimpleNamespace

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.openai_client import EMBED_MODEL, openai
from app.core.supabase_client import supabase
from app.models.profile import ProfileCreate, ProfileUpdate, ProfileDB

router = APIRouter(prefix="/profile", tags=["profile"])


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


async def create_embeddings(profile: ProfileCreate):
    """
    Create or update a user profile: compute embedding from company_name, company_description, and topic_list,
    then upsert the record into Supabase.
    """
    # Build input text for embedding
    combined = f"{profile.company_name}. {profile.company_description}." f" Topics: {', '.join(profile.topic_list)}" f" Topics: {', '.join(profile.countries)}"
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
    return embedding

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_profile(profile: ProfileCreate):
    embedding = await create_embeddings(profile)

    # Upsert into Supabase
    payload = profile.model_dump()

    payload["id"] = str(payload["id"])
    payload["embedding"] = embedding

    try:
        supabase.table("profiles").upsert(payload).execute()
        logger.info("Successfully upserted profile %s", payload["id"])
    except Exception as e:
        logger.error("Supabase upsert failed for profile %s: %s", payload["id"], e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Supabase upsert failed") from e

    # 3. Upsert profile-topic relationships
    # Convert profile_id to string for consistency
    profile_id = payload["id"]
    topic_ids = profile.topic_list

    try:
        supabase.table("profiles_to_topics").delete().eq("profile_id", profile_id).execute()

        # Fetch topic names for provided IDs
        topics_resp = supabase.table("meeting_topics") \
            .select("id, topic") \
            .in_("id", topic_ids) \
            .execute()

        topics_data = topics_resp.data or []
        # Prepare records for linking table
        link_records = [
            {"profile_id": profile_id, "topic_id": item["id"], "topic": item["topic"]}
            for item in topics_data
        ]

        if link_records:
            supabase.table("profiles_to_topics").insert(link_records).execute()
            logger.info(
                "Linked profile %s to topics %s",
                profile_id,
                [item["id"] for item in topics_data]
            )
        else:
            logger.warning(
                "No valid topics found for profile %s, provided IDs: %s",
                profile_id, topic_ids
            )
    except Exception as e:
        logger.error(
            "Error linking topics for profile %s: %s",
            profile_id, e
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={"status": "created"}
    )

@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=ProfileDB)
def get_user_profile(user_id: str) -> JSONResponse:
    try:
        result = (supabase.table("profiles")
                  .select("*")
                  .eq("id", user_id)
                  .execute())
        if len(result.data) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        return JSONResponse(status_code=status.HTTP_200_OK, content=result.data[0])
    except Exception as e:
        logger.error("Supabase select failed for profile %s: %s", user_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="Supabase select failed") from e


@router.patch("/{user_id}", status_code=status.HTTP_200_OK, response_model=ProfileDB)
async def update_user_profile(user_id: str, profile: ProfileUpdate) -> JSONResponse:
    try:
        payload = profile.model_dump(exclude_unset=True)

        result = (supabase.table("profiles")
                  .update(payload)
                  .eq("id", user_id)
                  .execute())
        if len(result.data) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        if (profile.topic_list is not None
                or profile.company_name is not None
                or profile.company_description is not None
                or profile.countries is not None):
            embedding_payload = {
                "embedding": await create_embeddings(SimpleNamespace(result.data[0]))
            }
            result = (supabase.table("profiles")
                      .update(embedding_payload)
                      .eq("id", user_id)
                      .execute())
            if len(result.data) == 0:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
        
        if (profile.topic_list is not None):
            profile_id = user_id
            topic_ids = profile.topic_list
            try:
                supabase.table("profiles_to_topics").delete().eq("profile_id", user_id).execute()

                # Fetch topic names for provided IDs
                topics_resp = supabase.table("meeting_topics") \
                    .select("id, topic") \
                    .in_("id", topic_ids) \
                    .execute()

                topics_data = topics_resp.data or []
                # Prepare records for linking table
                link_records = [
                    {"profile_id": profile_id, "topic_id": item["id"], "topic": item["topic"]}
                    for item in topics_data
                ]

                if link_records:
                    supabase.table("profiles_to_topics").insert(link_records).execute()
                    logger.info(
                        "Linked profile %s to topics %s",
                        profile_id,
                        [item["id"] for item in topics_data]
                    )
                else:
                    logger.warning(
                        "No valid topics found for profile %s, provided IDs: %s",
                        profile_id, topic_ids
                    )
            except Exception as e:
                logger.error(
                    "Error linking topics for profile %s: %s",
                    profile_id, e
                )
        return JSONResponse(status_code=status.HTTP_200_OK, content=result.data[0])
    except Exception as e:
        logger.error("Supabase update failed for profile %s: %s", user_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Supabase update failed") from e
