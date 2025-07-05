from typing import Literal, Optional

from pydantic import UUID4, BaseModel

class Company(BaseModel):
    role: str
    name: str
    description: Optional[str] = None
    company_stage: str
    company_size: int
    industry: str

class Politician(BaseModel):
    role: str
    further_information: str
    institution: str
    area_of_expertise: str

class ProfileCreate(BaseModel):
    id: UUID4
    name: str
    surname: str
    user_type: Literal["entrepreneur", "politician"]
    company: Optional[Company] = None
    politician: Optional[Politician] = None
    topic_ids: list[str]
    countries: list[str]
    newsletter_frequency: Literal["daily", "weekly", "none"]


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    user_type: Optional[Literal["entrepreneur", "politician"]] = None
    company: Optional[Company] = None
    politician: Optional[Politician] = None
    topic_ids: Optional[list[str]] = None
    countries: Optional[list[str]] = None
    newsletter_frequency: Optional[Literal["daily", "weekly", "none"]] = None


class ProfileReturn(ProfileCreate):
    embedding: list[float]
