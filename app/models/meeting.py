from datetime import date

from pydantic import BaseModel


class Meeting(BaseModel):
    date: date
    name: str
    tags: list[str]
