from pydantic import UUID4, BaseModel


class ProfileCreate(BaseModel):
    id: UUID4
    name: str
    surname: str
    company_name: str
    company_description: str
    topic_list: list[str]


class ProfileDB(ProfileCreate):
    embedding: list[float]
