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


async def create_embeddings(user_id: str, embedding_input: str):
    """
    Create or update a user profile: compute embedding from company_name, company_description, and topic_ids,
    then upsert the record into Supabase.
    """
    try:
        logger.info("Requesting embedding from OpenAI for profile %s", user_id)
        resp = openai.embeddings.create(input=[embedding_input], model=EMBED_MODEL)
        embedding = resp.data[0].embedding
        logger.info("Received embedding for profile %s", user_id)
    except Exception as e:
        logger.error("Embedding generation failed for profile %s: %s", user_id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Embedding generation failed"
        ) from e
    return embedding


def generate_user_interest_embedding_input(profile, topics):
    prompt = "Generate a concise and engaging text about this user’s interests based on their profile:"
    is_entrepreneur = profile["user_type"] == "entrepreneur"
    if is_entrepreneur:
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
        - Area of Expertise: {', '.join(profile["politician"]["area_of_expertise"])}
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
    """
    if is_entrepreneur:
        prompt += """
        - focus on their company and industry.
        """
    else:
        prompt += """
        - focus on their institution, expertise, and priorities.
        """

    response = openai.responses.create(model="gpt-4o", input=prompt)
    return response.output_text


def link_topics_to_user(topic_ids: list[str], user_id: str):
    supabase.table("profiles_to_topics").delete().eq("profile_id", user_id).execute()
    # Fetch topic names for provided IDs
    topics_resp = supabase.table("meeting_topics").select("id, topic").in_("id", topic_ids).execute()
    topics_data = topics_resp.data or []
    # Prepare records for linking table
    link_records = [
        {"profile_id": user_id, "topic_id": item["id"], "topic": item["topic"]} for item in topics_data
    ]
    if link_records:
        supabase.table("profiles_to_topics").insert(link_records).execute()
        logger.info("Linked profile %s to topics %s", user_id, [item["id"] for item in topics_data])
    else:
        logger.warning("No valid topics found for profile %s, provided IDs: %s", user_id, topic_ids)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_profile(profile: ProfileCreate) -> JSONResponse:
    # Upsert into Supabase
    payload = profile.model_dump()

    payload["id"] = str(payload["id"])
    user_id = payload["id"]

    topic_ids = payload.pop("topic_ids")
    topics = supabase.table("meeting_topics").select("id, topic").in_("id", topic_ids).execute()
    topics = [item["topic"] for item in topics.data] if topics.data else []

    embedding_input = generate_user_interest_embedding_input(payload, topics)
    payload["embedding_input"] = embedding_input
    embedding = await create_embeddings(user_id, embedding_input)
    payload["embedding"] = embedding

    company = payload.pop("company")
    politician = payload.pop("politician")
    is_entrepreneur = profile.user_type == "entrepreneur"


    # Create company or politician
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
        logger.info("Successfully upserted profile %s", user_id)
    except Exception as e:
        logger.error("Supabase upsert failed for profile %s: %s", user_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Supabase upsert failed") from e


    try:
        link_topics_to_user(topic_ids, user_id)
    except Exception as e:
        logger.error("Error linking topics for profile %s: %s", user_id, e)

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=get_profile(user_id))


@router.patch("/{user_id}", status_code=status.HTTP_200_OK, response_model=ProfileReturn)
async def update_user_profile(user_id: str, profile: ProfileUpdate) -> JSONResponse:
    # try:
    payload = profile.model_dump(exclude_unset=True)

    company = payload.pop("company") if "company" in payload else None
    politician = payload.pop("politician") if "politician" in payload else None
    topic_ids = payload.pop("topic_ids") if "topic_ids" in payload else None

    # Fetch existing profile
    if payload == {}:
        existing_profile = supabase.table("profiles").select("*").eq("id", user_id).execute()
    else:
        existing_profile = supabase.table("profiles").update(payload).eq("id", user_id).execute()

    existing_profile = existing_profile.data[0] if existing_profile.data else None
    if existing_profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    should_update_company = company is not None and existing_profile["user_type"] == "entrepreneur"
    should_update_politician = politician is not None and existing_profile["user_type"] == "politician"
    should_update_embeddings = (should_update_company
                                or should_update_politician
                                or topic_ids is not None
                                or "countries" in payload)

    # Update company or politician information
    if should_update_company:
        try:
            supabase.table("companies").update(company).eq("id", existing_profile["company_id"]).execute()
        except Exception as e:
            logger.error("Error updating company %s: %s", existing_profile["company_id"], e)
    elif should_update_politician:
        try:
            supabase.table("politicians").update(politician).eq("id", existing_profile["politician_id"]).execute()
        except Exception as e:
            logger.error("Error updating company %s: %s", existing_profile["politician_id"], e)

    # Update interested topic
    if topic_ids is not None:
        try:
            link_topics_to_user(topic_ids, user_id)
        except Exception as e:
            logger.error("Error linking topics for profile %s: %s", user_id, e)

    # Update profile embedding
    if should_update_embeddings:
        existing_profile = get_profile(user_id)

        # Build input text for embedding
        topics = supabase.table("meeting_topics").select("id, topic").in_("id", existing_profile["topic_ids"]).execute()
        topics = [item["topic"] for item in topics.data] if topics.data else []

        embedding_input = generate_user_interest_embedding_input(existing_profile, topics)
        embedding = await create_embeddings(user_id, embedding_input)
        embedding_payload = {"embedding_input": embedding_input, "embedding": embedding}
        result = supabase.table("profiles").update(embedding_payload).eq("id", user_id).execute()
        if len(result.data) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=get_profile(user_id))
