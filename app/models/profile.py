from pydantic import UUID4, BaseModel


class ProfileCreate(BaseModel):
    id: UUID4
    name: str
    surname: str
    company_name: str
    company_description: str
    topic_list: list[str]
    subscribed_newsletter: bool

class ProfileUpdate(BaseModel):
    name: str | None = None
    surname: str | None = None
    company_name: str | None = None
    company_description: str | None = None
    topic_list: list[str] | None = None
    subscribed_newsletter: bool | None = None

class ProfileDB(ProfileCreate):
    embedding: list[float]
