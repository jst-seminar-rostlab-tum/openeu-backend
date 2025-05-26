import json

from fastapi import APIRouter, HTTPException
from openai import OpenAI

from app.core.config import Settings
from app.core.supabase_client import supabase
from app.models.profile import ProfileCreate, ProfileDB

router = APIRouter(prefix="/profile", tags=["profile"])

settings = Settings()
openai = OpenAI(api_key=settings.get_openai_api_key())
EMBED_MODEL = "text-embedding-ada-002"


@router.post("/", response_model=ProfileDB)
async def create_profile(profile: ProfileCreate):
    """
    Create or update a user profile: compute embedding from company_name, company_description, and topic_list,
    then upsert the record into Supabase.
    """
    # Build input text for embedding
    combined = f"{profile.company_name}. {profile.company_description}." f" Topics: {', '.join(profile.topic_list)}"

    # Generate embedding
    resp = openai.embeddings.create(input=[combined], model=EMBED_MODEL)
    embedding = resp.data[0].embedding

    # Upsert into Supabase
    payload = profile.model_dump()
    # Convert UUID to string for JSON serialization
    payload["id"] = str(payload["id"])
    payload["embedding"] = embedding

    print(payload)
    try:
        result = supabase.table("profiles").upsert(payload).execute()
    except Exception as e:
        # log or rethrow with more context
        raise HTTPException(status_code=500, detail=f"Supabase upsert failed: {e}") from e

    record = result.data[0]
    if isinstance(record.get("embedding"), str):
        record["embedding"] = json.loads(record["embedding"])

    return ProfileDB(**record)
