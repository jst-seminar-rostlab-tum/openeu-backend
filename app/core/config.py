import os

import requests
from dotenv import find_dotenv, load_dotenv
from pygit2 import Repository


class Settings:
    def __init__(self) -> None:
        load_dotenv(find_dotenv())

    def _get_branch_data(self) -> dict[str, dict[str, str | int]]:
        values = {}
        branch_list = requests.request(
            "GET",
            f"https://api.supabase.com/v1/projects/{self.get_supabase_project_id()}/branches",
            headers={
                "Authorization": "Bearer " + self.get_supabase_rest_key(),
            },
            data={},
        )
        branch_list_data = branch_list.json()
        for branch in branch_list_data:
            if branch["git_branch"] == self.get_git_branch():
                branch_data = requests.request(
                    "GET",
                    f"https://api.supabase.com/v1/branches/{branch['id']}",
                    headers={
                        "Authorization": "Bearer " + self.get_supabase_rest_key(),
                    },
                    data={},
                )
                branch_data_json = branch_data.json()
                values["branch"] = branch_data_json
                keys_data = requests.request(
                    "GET",
                    f"https://api.supabase.com/v1/projects/{branch_data_json['ref']}/api-keys",
                    headers={
                        "Authorization": "Bearer " + self.get_supabase_rest_key(),
                    },
                    data={},
                )
                keys_data_json = keys_data.json()
                for key in keys_data_json:
                    if key["name"] == "service_role":
                        values["key"] = key
        return values

    def get_supabase_project_url(self) -> str:
        value = os.getenv("SUPABASE_PROJECT_URL")
        if value is None:
            value = ""
        if self.is_pull_request():
            branch_data = self._get_branch_data()
            value = "https://" + str(branch_data["branch"]["db_host"])[3:]
        return value

    def get_supabase_api_key(self) -> str:
        value = os.getenv("SUPABASE_API_KEY")
        if value is None:
            value = ""
        if self.is_pull_request():
            branch_data = self._get_branch_data()
            value = str(branch_data["key"]["api_key"])
        return value

    def get_supabase_rest_key(self) -> str:
        value = os.getenv("SUPABASE_REST_KEY")
        if value is None:
            value = ""
        return value

    def get_supabase_jwt_secret(self) -> str:
        value = os.getenv("SUPABASE_JWT_SECRET")
        if value is None:
            raise ValueError(
                "SUPABASE_JWT_SECRET environment variable is not set. " "This is required for authentication."
            )
        return value

    def get_supabase_project_id(self) -> str:
        value = os.getenv("SUPABASE_PROJECT_ID")
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

    def get_twitter_api_key(self) -> str:
        value = os.getenv("TWITTER_API_KEY")
        if value is None:
            value = ""
        return value

    def get_disable_auth(self) -> bool:
        value = os.getenv("DISABLE_AUTH")
        if value is None:
            return False
        return value.lower() == "true"

    def is_production(self) -> bool:
        """
        Check if the application is running in a production environment.
        :return: True if in production, False otherwise.
        """
        return os.getenv("ENVIRONMENT") != "development"

    def get_cohere_api_key(self) -> str:
        value = os.getenv("COHERE_API_KEY")
        if value is None:
            value = ""
        return value
