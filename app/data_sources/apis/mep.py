import requests

from app.core.supabase_client import supabase
from app.models.person import Person

CURRENT_MEPS_ENDPOINT = "https://data.europarl.europa.eu/api/v2/meps/show-current"
MEPS_TABLE_NAME = "meps"


def fetch_current_meps() -> list[Person]:
    """
    Scrape MEP data from the European Parliament API.
    Returns a list of Person objects representing MEPs.
    """
    params = {
        "format": "application/ld+json",
        "offset": "0",
    }
    response = requests.get(
        CURRENT_MEPS_ENDPOINT,
        params=params,
        timeout=15,
    )
    response.raise_for_status()
    json_data = response.json()
    return [Person(**item) for item in json_data["data"]]


def fetch_and_store_current_meps():
    """
    Fetch current MEPs and store them in the database.
    """
    meps = fetch_current_meps()
    meps_dicts = [meps_dict.model_dump() for meps_dict in meps]

    supabase.table(MEPS_TABLE_NAME).insert(
        meps_dicts,
        upsert=True,
    ).execute()
