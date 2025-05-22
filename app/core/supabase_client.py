from app.core.config import Settings
from supabase.client import Client, create_client

settings = Settings()

supabase: Client = create_client(settings.get_supabase_project_url(), settings.get_supabase_api_key())
