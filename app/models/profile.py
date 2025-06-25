from typing import Literal

from pydantic import UUID4, BaseModel


class ProfileCreate(BaseModel):
    id: UUID4
    name: str
    surname: str
    company_name: str
    company_description: str
    topic_list: list[str]
    countries: list[str]
    newsletter_frequency: Literal["daily", "weekly", "none"]

class ProfileUpdate(BaseModel):
    name: str | None = None
    surname: str | None = None
    company_name: str | None = None
    company_description: str | None = None
    topic_list: list[str] | None = None
    countries: list[str] | None = None
    newsletter_frequency: Literal["daily", "weekly", "none"] | None = None

class ProfileDB(ProfileCreate):
    embedding: list[float]
