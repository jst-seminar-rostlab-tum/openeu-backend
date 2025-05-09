from typing import List, Optional

import requests
from pydantic import BaseModel, ConfigDict, Field

CURRENT_MEPS_ENDPOINT = "https://data.europarl.europa.eu/api/v2/meps/show-current"


class Person(BaseModel):
    """
    Model representing a Member of European Parliament (MEP).

    This model contains detailed information about each MEP
    as provided by the European Parliament API.
    """

    model_config = ConfigDict(populate_by_name=True)

    identifier: str  # unique MEP number
    id: str  # "person/{identifier}""
    type: str  # "Person"
    label: str  # Printable name
    familyName: str  # Last name
    givenName: str  # First name
    sortLabel: str
    country_of_representation: str = Field(
        alias="api:country-of-representation"
    )  # Country code, e.g. "DE"
    political_group: str = Field(alias="api:political-group")
    officialFamilyName: Optional[str] = (
        None  # Last name in the official language of the MEP
    )
    officialGivenName: Optional[str] = (
        None  # First name in the official language of the MEP
    )


def fetch_current_meps() -> List[Person]:
    """
    Scrape MEP data from the European Parliament API.
    Returns a list of Person objects representing MEPs.
    """
    params = {
        "format": "application/ld+json",
        "offset": 0,
    }
    response = requests.get(
        CURRENT_MEPS_ENDPOINT,
        params=params,
        timeout=15,
    )
    response.raise_for_status()
    json_data = response.json()
    return [Person(**item) for item in json_data["data"]]
