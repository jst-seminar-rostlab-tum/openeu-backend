from typing import Literal

from pydantic import UUID4, BaseModel


class ProfileCreate(BaseModel):
    id: UUID4
    name: str
    surname: str
    company_name: str
    company_description: str
    topic_id_list: list[str]
    countries: list[str]
    newsletter_frequency: Literal["daily", "weekly", "none"]


class ProfileUpdate(BaseModel):
    name: str | None = None
    surname: str | None = None
    company_name: str | None = None
    company_description: str | None = None
    topic_id_list: list[str] | None = None
    countries: list[str] | None = None
    newsletter_frequency: Literal["daily", "weekly", "none"] | None = None


class ProfileReturn(ProfileCreate):
    id: UUID4
    name: str
    surname: str
    company_name: str
    company_description: str
    countries: list[str]
    topic_ids: list[str]
    topics: list[str]
    newsletter_frequency: Literal["daily", "weekly", "none"]
    embedding: list[float]


class ProfileDB(ProfileCreate):
    id: UUID4
    name: str
    surname: str
    company_name: str
    company_description: str
    countries: list[str]
    newsletter_frequency: Literal["daily", "weekly", "none"]
    embedding: list[float]
