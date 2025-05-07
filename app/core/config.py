import os

from dotenv import find_dotenv, load_dotenv


class Settings:
    def __init__(self) -> None:
        load_dotenv(find_dotenv())

    @staticmethod
    def get_supabase_project_url() -> str:
        value = os.getenv("SUPABASE_PROJECT_URL")
        if value is None:
            value = ""
        return value

    @staticmethod
    def get_supabase_api_key() -> str:
        value = os.getenv("SUPABASE_API_KEY")
        if value is None:
            value = ""
        return value
