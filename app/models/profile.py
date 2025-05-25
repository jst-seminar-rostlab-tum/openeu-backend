from pydantic import BaseModel, UUID4
from typing import List


class ProfileCreate(BaseModel):
    id: UUID4
    name: str
    surname: str
    company_name: str
    company_description: str
    topic_list: List[str]

class ProfileDB(ProfileCreate):
    embedding: List[float]