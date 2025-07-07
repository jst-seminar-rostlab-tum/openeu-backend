from typing import Literal, Optional

from pydantic import UUID4, BaseModel

class CompanyCreate(BaseModel):
    role: str
    name: str
    description: Optional[str] = None
    company_stage: str
    company_size: int
    industry: str

class CompanyReturn(CompanyCreate):
    id: UUID4

class CompanyUpdate(BaseModel):
    role: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    company_stage: Optional[str] = None
    company_size: Optional[int] = None
    industry: Optional[str] = None

class PoliticianCreate(BaseModel):
    role: str
    further_information: str
    institution: str
    area_of_expertise: str

class PoliticianReturn(PoliticianCreate):
    id: UUID4

class PoliticianUpdate(BaseModel):
    role: Optional[str] = None
    further_information: Optional[str] = None
    institution: Optional[str] = None
    area_of_expertise: Optional[str] = None

class ProfileCreate(BaseModel):
    id: UUID4
    name: str
    surname: str
    user_type: Literal["entrepreneur", "politician"]
    company: Optional[CompanyCreate] = None
    politician: Optional[PoliticianCreate] = None
    topic_ids: list[str]
    countries: list[str]
    newsletter_frequency: Literal["daily", "weekly", "none"]


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    surname: Optional[str] = None
    user_type: Optional[Literal["entrepreneur", "politician"]] = None
    company: Optional[CompanyUpdate] = None
    politician: Optional[PoliticianUpdate] = None
    topic_ids: Optional[list[str]] = None
    countries: Optional[list[str]] = None
    newsletter_frequency: Optional[Literal["daily", "weekly", "none"]] = None


class ProfileReturn(ProfileCreate):
    company: Optional[CompanyReturn] = None
    politician: Optional[PoliticianReturn] = None
    embedding_input: str
    embedding: list[float]
