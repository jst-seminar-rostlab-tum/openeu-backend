import logging

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.openai_client import EMBED_MODEL, openai
from app.core.supabase_client import supabase
from app.models.profile import ProfileCreate, ProfileUpdate, ProfileReturn

router = APIRouter(prefix="/profile", tags=["profile"])

logger = logging.getLogger(__name__)


def get_profile(user_id):
    result_profile = supabase.table("v_profiles").select("*").eq("id", user_id).single().execute()
    if not result_profile.data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Profile with id '{user_id}' not found")
    return result_profile.data


@router.get("/{user_id}", status_code=status.HTTP_200_OK, response_model=ProfileReturn)
def get_user_profile(user_id: str) -> JSONResponse:
    try:
        return JSONResponse(status_code=status.HTTP_200_OK, content=get_profile(user_id))
    except Exception as e:
        logger.error("Supabase select failed for profile %s: %s", user_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Supabase select failed") from e


async def create_embeddings(profile: dict):
    """
    Create or update a user profile: compute embedding from company_name, company_description, and topic_ids,
    then upsert the record into Supabase.
    """
    # Build input text for embedding

    topics = supabase.table("meeting_topics").select("id, topic").in_("id", profile["topic_ids"]).execute()
    print("Topics fetched:", topics)
    topics = [item["topic"] for item in topics.data] if topics.data else []

    prompt = "Generate a concise and engaging text about this user’s interests based on their profile:"

    if profile["user_type"] == "entrepreneur":
        prompt += f"""
        - Company Role: {profile["company"]["role"]}
        - Company Name: {profile["company"]["name"]}
        - Company Description: {profile["company"]["description"]}
        - Company Stage: {profile["company"]["company_stage"]}
        - Company Size: {profile["company"]["company_size"]}
        - Industry: {profile["company"]["industry"]}
        """
    else:
        prompt += f"""
        If politician:
        - Political Role: {profile["politician"]["role"]}
        - Institution: {profile["politician"]["institution"]}
        - Area of Expertise: {profile["politician"]["area_of_expertise"]}
        - Further Information: {profile["politician"]["further_information"]}
        """

    prompt += f"""
    Topics of Interest: {', '.join(topics)}
    Countries of Interest: {', '.join(profile["countries"])}
    
    Your task:
    - Summarizing the user's interests in about 100 words.
    - Try to enrich the text with relevant information from the provided fields.
    - Highlight their role, focus areas, and relevant topics.
    - Make the tone professional and neutral.
    - If entrepreneur, focus on their company and industry.
    - If politician, focus on their institution, expertise, and priorities.
    """

    response = openai.responses.create(model="gpt-4o", input=prompt)

    # Generate embedding
    try:
        logger.info("Requesting embedding from OpenAI for profile %s", profile["id"])
        resp = openai.embeddings.create(input=[response.output_text], model=EMBED_MODEL)
        embedding = resp.data[0].embedding
        logger.info("Received embedding for profile %s", profile["id"])
    except Exception as e:
        logger.error("Embedding generation failed for profile %s: %s", profile["id"], e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Embedding generation failed"
        ) from e
    return embedding


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_profile(profile: ProfileCreate) -> ProfileReturn:
    # Upsert into Supabase
    payload = profile.model_dump()
    embedding = await create_embeddings(payload)

    topic_ids = payload.pop("topic_ids")

    payload["id"] = str(payload["id"])
    payload["embedding"] = embedding

    company = payload.pop("company")
    politician = payload.pop("politician")
    is_entrepreneur = profile.user_type == "entrepreneur"

    # Create comp
    try:
        if is_entrepreneur:
            result = supabase.table("companies").upsert(company).execute()
        else:
            result = supabase.table("politicians").upsert(politician).execute()
    except Exception as e:
        logger.error("Supabase upsert failed for %s %s: %s",
                     "companies" if is_entrepreneur else "politicians",
                     company if is_entrepreneur else politician,
                     e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Supabase upsert failed") from e

    # Link profile to company or politician
    if is_entrepreneur:
        payload["company_id"] = result.data[0]["id"]
    else:
        payload["politician_id"] = result.data[0]["id"]

    try:
        supabase.table("profiles").upsert(payload).execute()
        logger.info("Successfully upserted profile %s", payload["id"])
    except Exception as e:
        logger.error("Supabase upsert failed for profile %s: %s", payload["id"], e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Supabase upsert failed") from e

    # Upsert profile-topic relationships
    # Convert profile_id to string for consistency
    profile_id = payload["id"]

    try:
        supabase.table("profiles_to_topics").delete().eq("id", profile_id).execute()

        # Fetch topic names for provided IDs
        topics_resp = supabase.table("meeting_topics").select("id, topic").in_("id", topic_ids).execute()

        topics_data = topics_resp.data or []
        # Prepare records for linking table
        link_records = [
            {"profile_id": profile_id, "topic_id": item["id"], "topic": item["topic"]} for item in topics_data
        ]

        if link_records:
            supabase.table("profiles_to_topics").insert(link_records).execute()
            logger.info("Linked profile %s to topics %s", profile_id, [item["id"] for item in topics_data])
        else:
            logger.warning("No valid topics found for profile %s, provided IDs: %s", profile_id, topic_ids)
    except Exception as e:
        logger.error("Error linking topics for profile %s: %s", profile_id, e)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=get_profile(profile_id))


@router.patch("/{user_id}", status_code=status.HTTP_200_OK, response_model=ProfileReturn)
async def update_user_profile(user_id: str, profile: ProfileUpdate) -> JSONResponse:
    # try:
    payload = profile.model_dump(exclude_unset=True)

    company = payload.pop("company")
    politician = payload.pop("politician")
    topic_ids = payload.pop("topic_ids") if "topic_ids" in payload else []

    existing_profile = supabase.table("profiles").update(payload).eq("id", user_id).execute()
    existing_profile = existing_profile.data[0] if existing_profile.data else None

    if existing_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    if company is not None and existing_profile["user_type"] == "entrepreneur":
        try:
            result = supabase.table("companies").update(company).eq("id", existing_profile["company_id"]).execute()
            company = result.data
        except Exception as e:
            logger.error("Error updating company %s: %s", existing_profile["company_id"], e)
    elif politician is not None and existing_profile["user_type"] == "politician":
        try:
            result = supabase.table("politicians").update(company).eq("id", existing_profile["politician_id"]).execute()
            politician = result.data
        except Exception as e:
            logger.error("Error updating company %s: %s", existing_profile["politician_id"], e)

    result_topics = None
    # Update interested topic
    if topic_ids is not None:
        profile_id = user_id
        try:
            supabase.table("profiles_to_topics").delete().eq("profile_id", user_id).execute()

            # Fetch topic names for provided IDs
            topics_resp = supabase.table("meeting_topics").select("id, topic").in_("id", topic_ids).execute()

            topics_data = topics_resp.data or []
            # Prepare records for linking table
            link_records = [
                {"profile_id": profile_id, "topic_id": item["id"], "topic": item["topic"]} for item in topics_data
            ]

            if link_records:
                result_topics = supabase.table("profiles_to_topics").insert(link_records).execute()
                result_topics = result_topics.data or []
                logger.info("Linked profile %s to topics %s", profile_id, [item["id"] for item in topics_data])
            else:
                logger.warning("No valid topics found for profile %s, provided IDs: %s", profile_id, topic_ids)
        except Exception as e:
            logger.error("Error linking topics for profile %s: %s", profile_id, e)

    if result_topics is None:
        result_topics = (
            supabase.table("profiles_to_topics")
            .select("topic_id, topic")
            .eq("profile_id", user_id)
            .execute()
        )

    topic_ids = [item["topic_id"] for item in result_topics or []]

    # Update profile data
    if payload:
        existing_profile = get_profile(user_id)
        print("profile ------- ", existing_profile)
        embedding_payload = {"embedding": await create_embeddings(existing_profile)}
        result = supabase.table("profiles").update(embedding_payload).eq("id", user_id).execute()
        if len(result.data) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    return JSONResponse(status_code=status.HTTP_200_OK, content=get_profile(user_id))
# except Exception as e:
#    logger.error("Supabase update failed for profile %s: %s", user_id, e)
#    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Supabase update failed") from e
