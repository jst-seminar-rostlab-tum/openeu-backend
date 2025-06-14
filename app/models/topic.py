from pydantic import BaseModel


class Topic(BaseModel):
    topic: str
