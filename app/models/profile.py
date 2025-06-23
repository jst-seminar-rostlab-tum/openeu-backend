from typing import Literal

from pydantic import UUID4, BaseModel


class ProfileCreate(BaseModel):
    id: UUID4
    name: str
    surname: str
    company_name: str
    company_description: str
    topic_list: list[str]
    newsletter_frequency: Literal["daily", "weekly", "none"]


class ProfileDB(ProfileCreate):
    embedding: list[float]
