import xml.etree.ElementTree as ET
from typing import List

import requests
from pydantic import BaseModel, ConfigDict


class Person(BaseModel):
    """
    Model representing a Member of European Parliament (MEP).

    This model contains detailed information about each MEP
    as provided by the European Parliament API.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str
    full_name: str
    country: str
    political_group: str
    national_political_group: str


def scrape_meps() -> List[Person]:
    """
    Scrape MEP data from the European Parliament API.
    Returns a list of Person objects representing MEPs.
    """
    url = "https://www.europarl.europa.eu/meps/en/full-list/xml"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    root = ET.fromstring(response.content)
    meps = []

    for mep_elem in root:
        person = Person(
            id=mep_elem.find("id").text,
            full_name=mep_elem.find("fullName").text,
            country=mep_elem.find("country").text,
            political_group=mep_elem.find("politicalGroup").text,
            national_political_group=mep_elem.find("nationalPoliticalGroup").text,
        )
        meps.append(person)

    return meps


print(scrape_meps())
