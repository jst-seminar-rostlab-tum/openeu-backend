from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Person(BaseModel):  # type: ignore
    """
    Model representing a Member of European Parliament (MEP).

    This model contains detailed information about each MEP
    as provided by the European Parliament API.
    """

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="identifier")  # unique MEP number
    type: str  # "Person"
    label: str  # Printable name
    family_name: str  # Last name
    given_name: str  # First name
    sort_label: str
    country_of_representation: str = Field(alias="api:country-of-representation")  # Country code, e.g. "DE"
    political_group: str = Field(alias="api:political-group")
    official_family_name: Optional[str] = None  # Last name in the official language of the MEP
    official_given_name: Optional[str] = None  # First name in the official language of the MEP
