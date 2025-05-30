import os

from dotenv import find_dotenv, load_dotenv
from pygit2 import Repository


class Settings:
    def __init__(self) -> None:
        load_dotenv(find_dotenv())

    def get_supabase_project_url(self) -> str:
        value = os.getenv("SUPABASE_PROJECT_URL")
        if value is None:
            value = ""
        return value

    def get_supabase_api_key(self) -> str:
        value = os.getenv("SUPABASE_API_KEY")
        if value is None:
            value = ""
        return value

    def get_crawler_api_key(self) -> str:
        value = os.getenv("CRAWLER_API_KEY")
        if value is None:
            value = ""
        return value

    def get_deepl_api_key(self) -> str:
        value = os.getenv("DEEPL_API_KEY")
        if value is None:
            value = ""
        return value

    def get_openai_api_key(self) -> str:
        value = os.getenv("OPENAI_API_KEY")
        if value is None:
            value = ""
        return value

    def get_brevo_api_key(self) -> str:
        value = os.getenv("BREVO_API_KEY")
        if value is None:
            value = ""
        return value

    def is_pull_request(self) -> bool:
        value = os.getenv("IS_PULL_REQUEST")
        if value is None:
            value = ""
        return value == "true"

    def get_git_branch(self) -> str:
        render = os.getenv("RENDER")
        value = Repository(".").head.shorthand if render is None else os.getenv("RENDER_GIT_BRANCH")
        if value is None:
            value = ""
        return value
