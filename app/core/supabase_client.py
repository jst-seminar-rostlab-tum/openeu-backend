from app.core.config import Settings
from supabase import Client, create_client  # type: ignore[attr-defined]


def get_client() -> Client:
    settings = Settings()
    return create_client(settings.get_supabase_project_url(), settings.get_supabase_api_key())
