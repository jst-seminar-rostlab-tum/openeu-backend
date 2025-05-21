import os
from app.core.config import Settings
from supabase import Client, create_client  # type: ignore[attr-defined]

settings = Settings()


SUPABASE_URL: str = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(settings.get_supabase_project_url(), settings.get_supabase_api_key())
